"""
Orchestration pipeline for generating evaluation reports.
"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .aggregator import StatsAggregator
from .generator import OverallEvaluator, ReportLLMClient, TraceEvaluator
from .pdf_exporter import PdfExportError, ReportPdfExporter
from .renderer import ReportRenderer

logger = logging.getLogger(__name__)


@dataclass
class ReportArtifacts:
    """Artifacts produced by the evaluation report pipeline."""

    html_path: Path
    pdf_path: Optional[Path] = None


class ReportPipeline:
    """
    Orchestrates the 5-stage evaluation pipeline:
    1. Per-Trace Analysis (LLM-PT)
    2. Rule-Based Aggregation
    3. Overall Analysis (LLM-OV)
    4. Data Preparation
    5. Report Rendering
    """

    def __init__(self, config: Dict[str, Any], output_dir: Path, api_key: str = None):
        self.config = config
        self.output_dir = output_dir
        self.client = ReportLLMClient(api_key=api_key)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.trace_evaluator = TraceEvaluator(self.client, config)
        self.aggregator = StatsAggregator(config)
        self.overall_evaluator = OverallEvaluator(self.client, config)
        self.renderer = ReportRenderer(output_dir)
        self.pdf_exporter = ReportPdfExporter(output_dir)

    async def run(
        self,
        trace_records: List[Dict[str, Any]],
        summary_records: Optional[List[Dict[str, Any]]] = None,
    ) -> ReportArtifacts:
        """
        Run the full pipeline.
        
        Args:
            trace_records: Detailed trace payloads (per-trace artifacts) used for LLM-PT
            summary_records: Lightweight trace summaries (from `trace_summary.jsonl`). When omitted,
                ``trace_records`` are re-used for aggregation.
            
        Returns:
            Path to the generated HTML report
        """
        logger.info("🚀 Starting Evaluation Report Pipeline")
        traces_for_rules = summary_records or trace_records
        
        # Stage 1: Per-Trace Analysis (Parallel)
        logger.info(f"Stage 1: Running LLM-PT on {len(trace_records)} traces...")
        pt_results = await self._run_pt_evaluations(trace_records)
        
        # Stage 2: Aggregation
        logger.info("Stage 2: Aggregating statistics...")
        rule_based_data = self.aggregator.aggregate(pt_results, traces_for_rules)
        
        # Stage 3: Overall Analysis
        logger.info("Stage 3: Running LLM-OV analysis...")
        llm_ov_data = await self.overall_evaluator.analyze(rule_based_data)
        if "error" in llm_ov_data:
            logger.warning(f"LLM-OV finished with error: {llm_ov_data['error']}")
            # Continue rendering even if OV fails (partial report is better than none)
        
        # Stage 4 & 5: Render
        logger.info("Stage 4 & 5: Rendering HTML report...")
        report_path = self.renderer.render(
            rule_based_data, llm_ov_data, traces_for_rules, self.config
        )
        
        pdf_path: Optional[Path] = None
        try:
            pdf_path = self.pdf_exporter.export(report_path)
        except PdfExportError as exc:
            logger.warning("PDF export failed: %s", exc)

        logger.info("✅ Pipeline Complete! Report: %s", report_path)
        if pdf_path:
            logger.info("✅ PDF ready: %s", pdf_path)

        return ReportArtifacts(html_path=report_path, pdf_path=pdf_path)

    async def _run_pt_evaluations(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run TraceEvaluator concurrently."""
        tasks = []
        for trace in traces:
            tasks.append(self.trace_evaluator.evaluate_trace(trace))
            
        # Use gather to run in parallel
        # TODO: Add semaphore/rate-limiting if needed (LLMClient handles raw calls, but concurrency limit might be needed)
        results = await asyncio.gather(*tasks)
        return list(results)

