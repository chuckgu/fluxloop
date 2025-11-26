"""Utilities for exporting the rendered HTML report as a PDF."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - import guard exercised via tests/log statements
    from weasyprint import CSS, HTML  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - handled gracefully at runtime
    HTML = None  # type: ignore
    CSS = None  # type: ignore

logger = logging.getLogger(__name__)


class PdfExportError(RuntimeError):
    """Raised when PDF generation fails."""


class ReportPdfExporter:
    """Converts the generated HTML report into a PDF file."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def export(self, html_report: Path) -> Optional[Path]:
        """Render ``report.html`` to ``report.pdf`` if WeasyPrint is available."""

        if HTML is None:
            logger.info(
                "WeasyPrint is not installed; skipping PDF export for %s", html_report
            )
            return None

        if not html_report.exists():
            raise PdfExportError(f"HTML report not found at {html_report}")

        pdf_path = self.output_dir / "report.pdf"
        try:
            stylesheets = [CSS(string=self._default_portrait_css())] if CSS else None
            HTML(filename=str(html_report), base_url=str(html_report.parent)).write_pdf(
                target=str(pdf_path),
                stylesheets=stylesheets,
            )
            logger.info("📄 PDF report generated at %s", pdf_path)
        except Exception as exc:  # pragma: no cover - depends on external renderer
            raise PdfExportError(f"Failed to generate PDF: {exc}") from exc

        return pdf_path

    def _default_portrait_css(self) -> str:
        """Ensure the PDF renders in portrait mode for better readability."""

        return """
        @page {
            size: A4 portrait;
            margin: 15mm;
        }

        html, body {
            width: 100%;
            height: auto;
        }

        .page-break {
            page-break-after: always;
        }
        """

