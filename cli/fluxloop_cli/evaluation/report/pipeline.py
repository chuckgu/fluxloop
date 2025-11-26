"""
Orchestration pipeline for generating evaluation reports.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List

from .aggregator import StatsAggregator
from .generator import OverallEvaluator, ReportLLMClient, TraceEvaluator
from .renderer import ReportRenderer

logger = logging.getLogger(__name__)


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

    async def run(self, trace_summaries: List[Dict[str, Any]]) -> Path:
        """
        Run the full pipeline.
        
        Args:
            trace_summaries: List of raw trace summary objects (from simulation output)
            
        Returns:
            Path to the generated HTML report
        """
        logger.info("🚀 Starting Evaluation Report Pipeline")
        
        # Stage 1: Per-Trace Analysis (Parallel)
        logger.info(f"Stage 1: Running LLM-PT on {len(trace_summaries)} traces...")
        pt_results = await self._run_pt_evaluations(trace_summaries)
        
        # Stage 2: Aggregation
        logger.info("Stage 2: Aggregating statistics...")
        rule_based_data = self.aggregator.aggregate(pt_results, trace_summaries)
        
        # Stage 3: Overall Analysis
        logger.info("Stage 3: Running LLM-OV analysis...")
        llm_ov_data = await self.overall_evaluator.analyze(rule_based_data)
        if "error" in llm_ov_data:
            logger.warning(f"LLM-OV finished with error: {llm_ov_data['error']}")
            # Continue rendering even if OV fails (partial report is better than none)
        
        # Stage 4 & 5: Render
        logger.info("Stage 4 & 5: Rendering HTML report...")
        report_path = self.renderer.render(rule_based_data, llm_ov_data, trace_summaries, self.config)
        
        logger.info(f"✅ Pipeline Complete! Report: {report_path}")
        return report_path

    async def _run_pt_evaluations(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run TraceEvaluator concurrently."""
        tasks = []
        for trace in traces:
            tasks.append(self.trace_evaluator.evaluate_trace(trace))
            
        # Use gather to run in parallel
        # TODO: Add semaphore/rate-limiting if needed (LLMClient handles raw calls, but concurrency limit might be needed)
        results = await asyncio.gather(*tasks)
        return list(results)

