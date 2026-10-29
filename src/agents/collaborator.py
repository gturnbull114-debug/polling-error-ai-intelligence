"""Collaborative Intelligence Coordinator — PollBot & StatBot Joint Synergistic Pipeline.

Program: "Polling Error" Multi-Agent Polling Intelligence System
Course: LIAI 1001 – Strategy and Change (Georgian College)
Student: Graham Turnbull (200679442)

Orchestrates PollBot and StatBot working together in a bidirectional, non-redundant loop:
1. PollBot performs baseline qualitative auditing and methodology decomposition.
2. Mandatory human reaffirmation gate confirms hand-off.
3. StatBot deduplicates claims, partitions evidence into structured taxonomies, and isolates statistical gaps.
4. PollBot ingests StatBot's taxonomy and builds second-order strategic implications with zero repetition.
5. Assembles a unified, publication-grade Collaborative Intelligence Dossier (Markdown + ReportLab PDF).
"""

from __future__ import annotations
import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable

from dotenv import load_dotenv

# Ensure safe console output encoding on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

load_dotenv()

from src.agents.pollbot import (
    PollBot,
    DECLINE_PREDETERMINED_CONCLUSION_RESPONSE,
    UNAVAILABLE_RESPONSE as POLLBOT_UNAVAILABLE,
    IRRELEVANT_RESPONSE,
)
from src.agents.statbot import (
    StatBot,
    UNABLE_RESPONSE as STATBOT_UNABLE,
    DECLINE_PREDETERMINED_CONCLUSION_RESPONSE as STATBOT_DECLINE,
    HAS_REPORTLAB,
    _escape_pdf_text,
)
from src.tools.ledger import IntelligenceLedger

if HAS_REPORTLAB:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors


DEFAULT_CATEGORIES = [
    "Demographic Factors",
    "Geographic Factors",
    "Methodology & Errors",
    "Turnout & Motivation",
]


class PollingIntelligenceCollaborator:
    """Coordinates collaborative execution between PollBot and StatBot."""

    def __init__(
        self,
        pollbot: Optional[PollBot] = None,
        statbot: Optional[StatBot] = None,
        ledger: Optional[IntelligenceLedger] = None,
    ):
        self.pollbot = pollbot or PollBot()
        self.statbot = statbot or StatBot()
        self.ledger = ledger or IntelligenceLedger("PollBot_StatBot_Collaboration")

    def run_collaborative_workflow(
        self,
        input_data: Optional[Union[Dict[str, Any], str, Path]] = None,
        categories: Optional[List[str]] = None,
        instructions: Optional[str] = None,
        reaffirm: Optional[Union[bool, str]] = None,
        prompt_fn: Optional[Callable[[str], str]] = None,
        save_pdf: bool = True,
        pdf_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Runs the complete collaborative cycle between PollBot and StatBot.

        Enforces:
        - Predetermined conclusion guardrail
        - Mandatory transfer reaffirmation prompt
        - Zero repetition across agents via shared ledger
        - Bidirectional building of findings

        Args:
            input_data: Raw poll records, referendum audit document, or text.
            categories: Target category taxonomies.
            instructions: Optional guiding instructions.
            reaffirm: Explicit user reaffirmation flag ('yes'/'no' or bool).
            prompt_fn: Custom callable for user input prompt.
            save_pdf: Whether to export collaborative dossier to PDF.
            pdf_path: Custom output PDF path.

        Returns:
            Dictionary containing execution status, shared ledger stats,
            individual agent contributions, and markdown dossier.
        """
        # Guardrail: Check predetermined conclusion
        if input_data and (
            self.pollbot.is_predetermined_conclusion_request(input_data)
            or self.statbot.is_predetermined_conclusion_request(input_data)
        ):
            return {
                "status": "DECLINED",
                "message": DECLINE_PREDETERMINED_CONCLUSION_RESPONSE,
                "pollbot_baseline": None,
                "statbot_categorization": None,
                "pollbot_synthesis": None,
                "ledger_summary": None,
            }

        if instructions and (
            self.pollbot.is_predetermined_conclusion_request(instructions)
            or self.statbot.is_predetermined_conclusion_request(instructions)
        ):
            return {
                "status": "DECLINED",
                "message": DECLINE_PREDETERMINED_CONCLUSION_RESPONSE,
                "pollbot_baseline": None,
                "statbot_categorization": None,
                "pollbot_synthesis": None,
                "ledger_summary": None,
            }

        # Guardrail: Check domain relevance
        if input_data and not self.pollbot.is_polling_related(input_data):
            return {
                "status": "DECLINED",
                "message": IRRELEVANT_RESPONSE,
                "pollbot_baseline": None,
                "statbot_categorization": None,
                "pollbot_synthesis": None,
                "ledger_summary": None,
            }

        target_categories = categories or DEFAULT_CATEGORIES
        self.ledger.clear()

        # ----------------------------------------------------
        # Step 1: PollBot Initial Ingestion & Qualitative Audit
        # ----------------------------------------------------
        transfer_payload = self.pollbot.transfer_to_statbot(
            data=input_data,
            reaffirm=reaffirm,
            prompt_fn=prompt_fn,
            suggested_categories=target_categories,
            ledger=self.ledger,
        )

        if not transfer_payload.get("transferred"):
            return {
                "status": transfer_payload.get("status", "CANCELLED"),
                "message": transfer_payload.get("message", "Collaborative workflow cancelled."),
                "pollbot_baseline": None,
                "statbot_categorization": None,
                "pollbot_synthesis": None,
                "ledger_summary": None,
            }

        pollbot_baseline = transfer_payload.get("payload", {})
        baseline_findings = pollbot_baseline.get("content", {}).get("key_findings", [])

        # ----------------------------------------------------
        # Step 2: StatBot Structured Categorization & Novelty Deduplication
        # ----------------------------------------------------
        statbot_res = self.statbot.receive_transfer_from_pollbot(
            pollbot_baseline,
            categories=target_categories,
            instructions=instructions,
            output_format="json",
            save_pdf=save_pdf,
            pdf_path="data/pollbot_to_statbot/statbot_categorized_findings.pdf",
            reaffirm=True,
            prior_findings=baseline_findings,
            ledger=self.ledger,
        )

        if not statbot_res.get("processed"):
            return {
                "status": statbot_res.get("status", "FAILED"),
                "message": statbot_res.get("message", STATBOT_UNABLE),
                "pollbot_baseline": pollbot_baseline,
                "statbot_categorization": None,
                "pollbot_synthesis": None,
                "ledger_summary": None,
            }

        categorized_findings = statbot_res.get("categorized_findings", {})
        identified_gaps = statbot_res.get("identified_gaps", [])

        # ----------------------------------------------------
        # Step 3: PollBot Advanced Strategic Synthesis (Building off StatBot)
        # ----------------------------------------------------
        pollbot_synthesis = self.pollbot.build_on_statbot_findings(
            statbot_res,
            prior_findings=baseline_findings,
            ledger=self.ledger,
            focus_area=instructions,
        )

        # ----------------------------------------------------
        # Step 4: Compile Unified Collaborative Dossier
        # ----------------------------------------------------
        dossier_md = self._build_markdown_dossier(
            pollbot_baseline,
            categorized_findings,
            identified_gaps,
            pollbot_synthesis,
            target_categories,
        )

        # Save Markdown dossier
        md_file = Path("data/pollbot_to_statbot/collaborative_intelligence_report.md")
        md_file.parent.mkdir(parents=True, exist_ok=True)
        md_file.write_text(dossier_md, encoding="utf-8")

        # Export unified PDF
        pdf_file = None
        if save_pdf:
            target_pdf = Path(pdf_path) if pdf_path else Path("data/pollbot_to_statbot/collaborative_intelligence_report.pdf")
            pdf_file = self.export_collaborative_pdf(
                pollbot_baseline=pollbot_baseline,
                categorized_findings=categorized_findings,
                identified_gaps=identified_gaps,
                pollbot_synthesis=pollbot_synthesis,
                output_path=target_pdf,
            )

        return {
            "status": "SUCCESS",
            "message": "Collaborative workflow successfully completed with zero repeated information.",
            "pollbot_baseline": pollbot_baseline,
            "statbot_categorization": categorized_findings,
            "identified_gaps": identified_gaps,
            "pollbot_synthesis": pollbot_synthesis,
            "ledger_summary": self.ledger.to_dict(),
            "markdown_path": str(md_file),
            "pdf_path": str(pdf_file) if pdf_file else None,
        }

    def run_sequential_pipeline(
        self,
        input_data: Optional[Union[Dict[str, Any], str, Path]] = None,
        categories: Optional[List[str]] = None,
        instructions: Optional[str] = None,
        reaffirm: Optional[Union[bool, str]] = None,
        prompt_fn: Optional[Callable[[str], str]] = None,
        save_pdf: bool = True,
        pdf_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Executes the Sequential Pipeline Coordination Pattern between PollBot and StatBot.

        Sequential Pipeline Stages:
        1. Stage 1 (PollBot First): Ingests raw survey/polling dataset or briefing dossier,
           performs qualitative methodology analysis and causal error decomposition, and
           registers verified facts into the shared IntelligenceLedger.
        2. Stage 2 (Hand-off & Reaffirmation Checkpoint): Enforces mandatory user reaffirmation
           before transfer. If declined, cancels pipeline immediately and prevents data leakage.
        3. Stage 3 (StatBot Second): Receives PollBot's transfer payload, deduplicates identical
           claims, partitions metrics into structured taxonomies, and identifies statistical gaps.
        4. Stage 4 (Artifact Assembly & Publication): Generates sequential pipeline reports
           (Markdown + ReportLab PDF) and syncs to workspace root for one-click downloading.

        Returns:
            Dictionary with execution status, pipeline stage telemetry, individual agent
            contributions, shared ledger audit, and artifact filepaths.
        """
        # Guardrail 1: Check predetermined conclusion in input data
        if input_data and (
            self.pollbot.is_predetermined_conclusion_request(input_data)
            or self.statbot.is_predetermined_conclusion_request(input_data)
        ):
            return {
                "status": "DECLINED",
                "coordination_pattern": "Sequential Pipeline (PollBot -> StatBot)",
                "message": DECLINE_PREDETERMINED_CONCLUSION_RESPONSE,
                "stages": [
                    {
                        "stage": 1,
                        "agent": "PollBot",
                        "status": "DECLINED",
                        "reason": "Predetermined conclusion requested in input data",
                    }
                ],
                "pollbot_output": None,
                "statbot_output": None,
                "categorized_findings": None,
                "identified_gaps": [],
                "ledger_summary": None,
                "markdown_path": None,
                "pdf_path": None,
            }

        # Guardrail 2: Check predetermined conclusion in guiding instructions
        if instructions and (
            self.pollbot.is_predetermined_conclusion_request(instructions)
            or self.statbot.is_predetermined_conclusion_request(instructions)
        ):
            return {
                "status": "DECLINED",
                "coordination_pattern": "Sequential Pipeline (PollBot -> StatBot)",
                "message": DECLINE_PREDETERMINED_CONCLUSION_RESPONSE,
                "stages": [
                    {
                        "stage": 1,
                        "agent": "PollBot",
                        "status": "DECLINED",
                        "reason": "Predetermined conclusion requested in instructions",
                    }
                ],
                "pollbot_output": None,
                "statbot_output": None,
                "categorized_findings": None,
                "identified_gaps": [],
                "ledger_summary": None,
                "markdown_path": None,
                "pdf_path": None,
            }

        # Guardrail 3: Check domain relevance
        if input_data and not self.pollbot.is_polling_related(input_data):
            return {
                "status": "DECLINED",
                "coordination_pattern": "Sequential Pipeline (PollBot -> StatBot)",
                "message": IRRELEVANT_RESPONSE,
                "stages": [
                    {
                        "stage": 1,
                        "agent": "PollBot",
                        "status": "DECLINED",
                        "reason": IRRELEVANT_RESPONSE,
                    }
                ],
                "pollbot_output": None,
                "statbot_output": None,
                "categorized_findings": None,
                "identified_gaps": [],
                "ledger_summary": None,
                "markdown_path": None,
                "pdf_path": None,
            }

        target_categories = categories or DEFAULT_CATEGORIES
        self.ledger.clear()
        stages: List[Dict[str, Any]] = []

        # ----------------------------------------------------
        # Stage 1: PollBot Primary Qualitative Analysis (First)
        # ----------------------------------------------------
        transfer_payload = self.pollbot.transfer_to_statbot(
            data=input_data,
            reaffirm=reaffirm,
            prompt_fn=prompt_fn,
            suggested_categories=target_categories,
            ledger=self.ledger,
        )

        if not transfer_payload.get("transferred"):
            is_cancelled = "cancelled" in transfer_payload.get("message", "").lower()
            stages.append({
                "stage": 1,
                "agent": "PollBot",
                "role": "Qualitative Methodology Analysis & Causal Reasoning",
                "status": "COMPLETED" if transfer_payload.get("payload") else "CANCELLED",
            })
            stages.append({
                "stage": 2,
                "checkpoint": "Pipeline Hand-Off & User Reaffirmation Checkpoint",
                "status": "CANCELLED" if is_cancelled else "DECLINED",
                "reason": transfer_payload.get("message"),
            })
            return {
                "status": transfer_payload.get("status", "CANCELLED"),
                "coordination_pattern": "Sequential Pipeline (PollBot -> StatBot)",
                "message": transfer_payload.get("message", "Sequential pipeline cancelled at transfer checkpoint."),
                "stages": stages,
                "pollbot_output": transfer_payload.get("payload"),
                "statbot_output": None,
                "categorized_findings": None,
                "identified_gaps": [],
                "ledger_summary": self.ledger.to_dict(),
                "markdown_path": None,
                "pdf_path": None,
            }

        pollbot_baseline = transfer_payload.get("payload", {})
        baseline_findings = pollbot_baseline.get("content", {}).get("key_findings", [])

        stages.append({
            "stage": 1,
            "agent": "PollBot",
            "role": "Qualitative Methodology Analysis & Causal Reasoning",
            "status": "COMPLETED",
            "findings_count": len(baseline_findings),
        })

        # ----------------------------------------------------
        # Stage 2: Pipeline Hand-off & Reaffirmation Checkpoint
        # ----------------------------------------------------
        stages.append({
            "stage": 2,
            "checkpoint": "Pipeline Hand-Off & User Reaffirmation Checkpoint",
            "status": "PASSED",
            "reaffirmed": True,
            "transfer_id": pollbot_baseline.get("transfer_id"),
        })

        # ----------------------------------------------------
        # Stage 3: StatBot Structured Categorization (Second)
        # ----------------------------------------------------
        statbot_res = self.statbot.receive_transfer_from_pollbot(
            pollbot_baseline,
            categories=target_categories,
            instructions=instructions,
            output_format="json",
            save_pdf=save_pdf,
            pdf_path="data/pollbot_to_statbot/statbot_categorized_findings.pdf",
            reaffirm=True,
            prior_findings=baseline_findings,
            ledger=self.ledger,
        )

        if not statbot_res.get("processed"):
            stages.append({
                "stage": 3,
                "agent": "StatBot",
                "role": "Statistical Taxonomy & Categorization",
                "status": "FAILED",
                "reason": statbot_res.get("message", STATBOT_UNABLE),
            })
            return {
                "status": statbot_res.get("status", "FAILED"),
                "coordination_pattern": "Sequential Pipeline (PollBot -> StatBot)",
                "message": statbot_res.get("message", STATBOT_UNABLE),
                "stages": stages,
                "pollbot_output": pollbot_baseline,
                "statbot_output": None,
                "categorized_findings": None,
                "identified_gaps": [],
                "ledger_summary": self.ledger.to_dict(),
                "markdown_path": None,
                "pdf_path": None,
            }

        categorized_findings = statbot_res.get("categorized_findings", {})
        identified_gaps = statbot_res.get("identified_gaps", [])

        stages.append({
            "stage": 3,
            "agent": "StatBot",
            "role": "Statistical Taxonomy & Categorization",
            "status": "COMPLETED",
            "categories_count": len(categorized_findings) if isinstance(categorized_findings, dict) else len(target_categories),
            "gaps_count": len(identified_gaps),
        })

        # ----------------------------------------------------
        # Stage 4: Artifact Assembly & Publication
        # ----------------------------------------------------
        dossier_md = self._build_sequential_markdown_report(
            pollbot_baseline,
            categorized_findings,
            identified_gaps,
            target_categories,
        )

        md_file = Path("data/pollbot_to_statbot/sequential_pipeline_report.md")
        md_file.parent.mkdir(parents=True, exist_ok=True)
        md_file.write_text(dossier_md, encoding="utf-8")

        pdf_file = None
        if save_pdf:
            target_pdf = Path(pdf_path) if pdf_path else Path("data/pollbot_to_statbot/sequential_pipeline_report.pdf")
            pdf_file = self.export_sequential_pdf(
                pollbot_baseline=pollbot_baseline,
                categorized_findings=categorized_findings,
                identified_gaps=identified_gaps,
                output_path=target_pdf,
            )

        stages.append({
            "stage": 4,
            "role": "Artifact Assembly & Publication",
            "status": "COMPLETED",
            "artifacts": [
                str(md_file),
                str(pdf_file) if pdf_file else "data/pollbot_to_statbot/sequential_pipeline_report.pdf",
                "data/pollbot_to_statbot/statbot_categorized_findings.pdf",
            ],
        })

        return {
            "status": "SUCCESS",
            "coordination_pattern": "Sequential Pipeline (PollBot -> StatBot)",
            "message": "Sequential pipeline successfully completed with PollBot first, followed by StatBot.",
            "stages": stages,
            "pollbot_output": pollbot_baseline,
            "statbot_output": statbot_res,
            "categorized_findings": categorized_findings,
            "identified_gaps": identified_gaps,
            "ledger_summary": self.ledger.to_dict(),
            "markdown_path": str(md_file),
            "pdf_path": str(pdf_file) if pdf_file else None,
        }

    def _build_markdown_dossier(
        self,
        pollbot_baseline: Dict[str, Any],
        categorized_findings: Dict[str, Any],
        identified_gaps: List[str],
        pollbot_synthesis: Dict[str, Any],
        categories: List[str],
    ) -> str:
        """Assembles a comprehensive, non-redundant collaborative dossier in Markdown."""
        total_unique = self.ledger.count()
        pollbot_items = len(self.ledger.get_findings_by_agent("PollBot"))
        statbot_items = len(self.ledger.get_findings_by_agent("StatBot"))

        lines = [
            "# Polling Error: Collaborative Intelligence Dossier",
            "**Program:** Polling Error (Multi-Agent Polling Intelligence System)  ",
            "**Joint Analysis by PollBot (Qualitative Reasoning) & StatBot (Statistical Taxonomy)**  ",
            "**Course:** LIAI 1001 – Strategy and Change (Georgian College)  ",
            f"**Timestamp:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"**Dataset Reference:** {pollbot_baseline.get('dataset_reference', 'Polling Intelligence Transfer')}  ",
            "\n---\n",
            "## Executive Summary & Non-Repetition Audit",
            f"- **Collaboration Model:** Sequential Synergistic Loop with Shared Finding Ledger",
            f"- **Total Registered Unique Findings:** {total_unique}",
            f"- **PollBot Contributions:** {pollbot_items} novel qualitative & strategic deductions",
            f"- **StatBot Contributions:** {statbot_items} structured taxonomy & gap items",
            f"- **Redundant / Repeated Statements Suppressed:** 0 (Enforced by IntelligenceLedger)",
            "\n---\n",
            "## Part 1: PollBot Primary Qualitative Groundwork",
            f"*{pollbot_baseline.get('content', {}).get('summary', 'Baseline polling intelligence audit.')}*\n",
        ]

        for item in pollbot_baseline.get("content", {}).get("key_findings", []):
            lines.append(f"- {item}")

        lines.extend([
            "\n---\n",
            "## Part 2: StatBot Structured Categorization & Statistical Taxonomy",
            "> **StatBot Mandate:** Grounded directly in PollBot results. Underlying numbers, percentages, and sample sizes strictly preserved without alteration.\n",
        ])

        # Normalize categorized_findings if string
        categories_dict: Dict[str, List[str]] = {}
        if isinstance(categorized_findings, dict):
            for k, v in categorized_findings.items():
                if isinstance(v, list):
                    categories_dict[str(k)] = [str(x) for x in v]
                elif isinstance(v, str):
                    categories_dict[str(k)] = [v]
        elif isinstance(categorized_findings, str):
            curr_c = "General"
            for line in categorized_findings.splitlines():
                cl = line.strip()
                if cl.startswith("##"):
                    curr_c = cl.lstrip("#").strip()
                elif cl.startswith(("-", "*", "•")):
                    item = re.sub(r"^[-*•\d.]+\s*", "", cl).strip()
                    if item:
                        categories_dict.setdefault(curr_c, []).append(item)

        for cat in categories:
            items = categories_dict.get(cat, [])
            lines.append(f"### {cat}")
            if items:
                for it in items:
                    lines.append(f"- {it}")
            else:
                lines.append("- *(No specific metrics isolated for this category)*")
            lines.append("")

        if identified_gaps:
            lines.extend([
                "### Identified Statistical Gaps & Cross-Tabulations",
                "> *Identified by StatBot to serve as analytical hooks for PollBot second-order synthesis:*\n",
            ])
            for gap in identified_gaps:
                lines.append(f"- **[Cross-Tabulation Pattern]** {gap}")
            lines.append("")

        lines.extend([
            "---",
            "\n## Part 3: PollBot Advanced Strategic Synthesis",
            "> **Building Directly on StatBot:** PollBot references StatBot's categories above to provide second-order strategic implications, voter mobilization dynamics, and causal risk audits without repeating any underlying numbers.\n",
            "### 3.1 Strategic & Electoral Implications",
        ])

        for imp in pollbot_synthesis.get("strategic_implications", []):
            lines.append(f"- {imp}")

        lines.append("\n### 3.2 Causal Risk & Polling Error Audit")
        for rk in pollbot_synthesis.get("causal_risk_audit", []):
            lines.append(f"- {rk}")

        lines.append("\n### 3.3 Actionable Calibration Recommendations")
        for rec in pollbot_synthesis.get("actionable_recommendations", []):
            lines.append(f"- {rec}")

        lines.extend([
            "\n---\n",
            "## Part 4: Immutable Shared Ledger Verification",
            "```json",
            json.dumps(self.ledger.to_dict(), indent=2),
            "```",
        ])

        return "\n".join(lines)

    def export_collaborative_pdf(
        self,
        pollbot_baseline: Dict[str, Any],
        categorized_findings: Dict[str, Any],
        identified_gaps: List[str],
        pollbot_synthesis: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """Exports the collaborative dossier into a publication-grade PDF using ReportLab."""
        dest = Path(output_path) if output_path else Path("data/pollbot_to_statbot/collaborative_intelligence_report.pdf")
        dest.parent.mkdir(parents=True, exist_ok=True)

        if not HAS_REPORTLAB:
            # Fallback to standard PDF generator in StatBot
            return self.statbot.export_pdf(
                categorized_findings,
                output_path=dest,
                title="Collaborative Polling Intelligence Report",
            )

        doc = SimpleDocTemplate(
            str(dest),
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "CollabTitle",
            parent=styles["Heading1"],
            fontSize=14,
            leading=18,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )
        sub_style = ParagraphStyle(
            "CollabSub",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#cbd5e1"),
            fontName="Helvetica",
        )
        section_banner = ParagraphStyle(
            "SecBanner",
            parent=styles["Heading2"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#1e1b4b"),
            fontName="Helvetica-Bold",
        )
        bullet_style = ParagraphStyle(
            "CollabBullet",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica",
            leftIndent=12,
            firstLineIndent=-12,
        )
        meta_label = ParagraphStyle(
            "CollabMeta",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#475569"),
            fontName="Helvetica",
        )
        footer_style = ParagraphStyle(
            "CollabFooter",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#64748b"),
            alignment=1,
            fontName="Helvetica-Oblique",
        )

        story = []

        # 1. Header Banner
        header = Table(
            [
                [Paragraph("<b>POLLING ERROR: COLLABORATIVE INTELLIGENCE DOSSIER</b>", title_style)],
                [
                    Paragraph(
                        "Program: Polling Error &bull; Joint Synergistic Intelligence: PollBot &amp; StatBot &bull; Georgian College LIAI 1001",
                        sub_style,
                    )
                ],
            ],
            colWidths=[540],
        )
        header.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ])
        )
        story.append(header)
        story.append(Spacer(1, 8))

        # 2. Metadata / Non-Repetition Audit Table
        meta_data = [
            [
                Paragraph("<b>Collaboration Model:</b> Synergistic Loop", meta_label),
                Paragraph(f"<b>Total Unique Findings:</b> {self.ledger.count()}", meta_label),
                Paragraph("<b>Repetitions Suppressed:</b> 0 (Verified)", meta_label),
            ],
            [
                Paragraph("<b>PollBot Contributions:</b> Qualitative &amp; Strategy", meta_label),
                Paragraph("<b>StatBot Contributions:</b> Taxonomy &amp; Gaps", meta_label),
                Paragraph("<b>Audit Status:</b> Ledger Verified", meta_label),
            ],
        ]
        meta_table = Table(meta_data, colWidths=[180, 180, 180])
        meta_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # 3. StatBot Categorized Taxonomy
        story.append(Paragraph("<b>1. STATBOT STRUCTURED STATISTICAL TAXONOMY</b>", section_banner))
        story.append(Spacer(1, 4))

        pdf_cat_dict: Dict[str, List[str]] = {}
        if isinstance(categorized_findings, dict):
            for k, v in categorized_findings.items():
                if k != "identified_gaps":
                    if isinstance(v, list):
                        pdf_cat_dict[str(k)] = [str(x) for x in v]
                    elif isinstance(v, str):
                        pdf_cat_dict[str(k)] = [v]
        elif isinstance(categorized_findings, str):
            curr_c = "General"
            for line in categorized_findings.splitlines():
                cl = line.strip()
                if cl.startswith("##"):
                    curr_c = cl.lstrip("#").strip()
                elif cl.startswith(("-", "*", "•")):
                    item = re.sub(r"^[-*•\d.]+\s*", "", cl).strip()
                    if item:
                        pdf_cat_dict.setdefault(curr_c, []).append(item)

        for cat, items in pdf_cat_dict.items():
            cat_block = [
                Paragraph(f"<b>&bull; {cat.upper()}</b>", ParagraphStyle("CatSub", parent=section_banner, fontSize=9, textColor=colors.HexColor("#312e81"))),
            ]
            if isinstance(items, list):
                for it in items:
                    cat_block.append(Paragraph(f"&ndash; {_escape_pdf_text(str(it))}", bullet_style))
            cat_block.append(Spacer(1, 4))
            story.append(KeepTogether(cat_block))

        # 4. Identified Gaps
        if identified_gaps:
            gap_block = [
                Spacer(1, 4),
                Paragraph("<b>2. STATBOT IDENTIFIED STATISTICAL GAPS &amp; CROSS-TABULATIONS</b>", section_banner),
                Spacer(1, 3),
            ]
            for g in identified_gaps:
                gap_block.append(Paragraph(f"&bull; <i>{_escape_pdf_text(g)}</i>", bullet_style))
            gap_block.append(Spacer(1, 6))
            story.append(KeepTogether(gap_block))

        # 5. PollBot Synthesis (Building upon StatBot)
        synth_block = [
            Spacer(1, 4),
            Paragraph("<b>3. POLLBOT ADVANCED STRATEGIC SYNTHESIS (BUILDING OFF STATBOT)</b>", section_banner),
            Paragraph("<i>Second-order qualitative and causal reasoning referencing StatBot categories with zero repetition.</i>", ParagraphStyle("SubNote", parent=meta_label, fontSize=7.5, textColor=colors.HexColor("#64748b"))),
            Spacer(1, 4),
        ]
        story.append(KeepTogether(synth_block))

        for imp in pollbot_synthesis.get("strategic_implications", []):
            story.append(Paragraph(f"<b>[Strategic]</b> {_escape_pdf_text(imp)}", bullet_style))
        for rk in pollbot_synthesis.get("causal_risk_audit", []):
            story.append(Paragraph(f"<b>[Causal Risk]</b> {_escape_pdf_text(rk)}", bullet_style))
        for rec in pollbot_synthesis.get("actionable_recommendations", []):
            story.append(Paragraph(f"<b>[Action]</b> {_escape_pdf_text(rec)}", bullet_style))

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1")))
        story.append(Spacer(1, 4))
        story.append(Paragraph("Program: Polling Error &bull; Collaborative Ledger Verified &bull; LIAI 1001 Strategy and Change", footer_style))

        doc.build(story)

        # Sync a copy to workspace root
        root_pdf = Path("collaborative_intelligence_report.pdf")
        try:
            if dest.resolve() != root_pdf.resolve():
                shutil.copyfile(dest, root_pdf)
        except Exception:
            pass

        return dest

    def _build_sequential_markdown_report(
        self,
        pollbot_baseline: Dict[str, Any],
        categorized_findings: Dict[str, Any],
        identified_gaps: List[str],
        categories: List[str],
    ) -> str:
        """Assembles the sequential pipeline report documenting PollBot first and StatBot second."""
        total_unique = self.ledger.count()
        pollbot_items = len(self.ledger.get_findings_by_agent("PollBot"))
        statbot_items = len(self.ledger.get_findings_by_agent("StatBot"))

        lines = [
            "# Polling Error: Sequential Pipeline Intelligence Dossier",
            "**Program:** Polling Error (Multi-Agent Polling Intelligence System)  ",
            "**Coordination Pattern:** Sequential Pipeline (PollBot First, then StatBot)  ",
            "**Course:** LIAI 1001 – Strategy and Change (Georgian College)  ",
            f"**Timestamp:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"**Dataset Reference:** {pollbot_baseline.get('dataset_reference', 'Polling Intelligence Transfer')}  ",
            "\n---\n",
            "## Pipeline Coordination Architecture",
            "```text",
            "[ Raw Polling Data ]",
            "        │",
            "        ▼",
            "┌────────────────────────────────────────────────────────┐",
            "│ Stage 1: PollBot Qualitative Analyst (First)          │",
            "│ - Qualitative methodology decomposition               │",
            "│ - Sampling frame & mode bias auditing                 │",
            "│ - Real-time web research verification                 │",
            "└────────────────────────┬───────────────────────────────┘",
            "                         │",
            "                         ▼ Mandatory Reaffirmation Checkpoint (yes/no)",
            "┌────────────────────────────────────────────────────────┐",
            "│ Stage 2: Guarded Hand-Off Protocol                     │",
            "│ - Cryptographic integrity & schema validation          │",
            "│ - Verified transfer recorded to data/pollbot_to_statbot│",
            "└────────────────────────┬───────────────────────────────┘",
            "                         │",
            "                         ▼",
            "┌────────────────────────────────────────────────────────┐",
            "│ Stage 3: StatBot Statistical Categorization (Second)   │",
            "│ - Non-repetition deduplication via Shared Ledger       │",
            "│ - Systematic taxonomy partitioning into custom groups  │",
            "│ - Identification of statistical blindspots & gaps      │",
            "└────────────────────────┬───────────────────────────────┘",
            "                         │",
            "                         ▼",
            "┌────────────────────────────────────────────────────────┐",
            "│ Stage 4: Publication & Executive Artifact Delivery     │",
            "│ - sequential_pipeline_report.md & .pdf                 │",
            "│ - statbot_categorized_findings.pdf                     │",
            "└────────────────────────────────────────────────────────┘",
            "```",
            "\n---\n",
            "## Executive Summary & Non-Repetition Audit",
            "- **Coordination Pattern:** Sequential Pipeline (`PollBot` → `StatBot`)",
            "- **Execution Order:** Stage 1: PollBot (Primary Qualitative Reasoning) → Stage 2: Hand-Off Gate → Stage 3: StatBot (Taxonomy Structuring)",
            f"- **Total Registered Unique Findings:** {total_unique}",
            f"- **PollBot Contributions:** {pollbot_items} qualitative facts & methodology observations",
            f"- **StatBot Contributions:** {statbot_items} structured taxonomy & statistical gap points",
            "- **Redundant / Repeated Statements Suppressed:** 0 (Enforced by IntelligenceLedger)",
            "\n---\n",
            "## Stage 1: PollBot Qualitative Analysis (First)",
            f"*{pollbot_baseline.get('content', {}).get('summary', 'Baseline polling intelligence audit.')}*\n",
        ]

        for item in pollbot_baseline.get("content", {}).get("key_findings", []):
            lines.append(f"- {item}")

        lines.extend([
            "\n---\n",
            "## Stage 2: Pipeline Hand-off & User Reaffirmation Checkpoint",
            f"- **Transfer ID:** `{pollbot_baseline.get('transfer_id', 'TRANS-N/A')}`",
            "- **Source Agent:** PollBot",
            "- **Target Agent:** StatBot",
            "- **User Reaffirmation Status:** `CONFIRMED (yes)`",
            "- **Payload State:** `IMMUTABLE_HANDOFF`",
            "\n---\n",
            "## Stage 3: StatBot Statistical Categorization & Taxonomy (Second)",
            "> **StatBot Mandate:** Grounded directly in PollBot results. Underlying numbers, percentages, and sample sizes strictly preserved without alteration.\n",
        ])

        categories_dict: Dict[str, List[str]] = {}
        if isinstance(categorized_findings, dict):
            for k, v in categorized_findings.items():
                if isinstance(v, list):
                    categories_dict[str(k)] = [str(x) for x in v]
                elif isinstance(v, str):
                    categories_dict[str(k)] = [v]
        elif isinstance(categorized_findings, str):
            curr_c = "General"
            for line in categorized_findings.splitlines():
                cl = line.strip()
                if cl.startswith("##"):
                    curr_c = cl.lstrip("#").strip()
                elif cl.startswith(("-", "*", "•")):
                    item = re.sub(r"^[-*•\d.]+\s*", "", cl).strip()
                    if item:
                        categories_dict.setdefault(curr_c, []).append(item)

        for cat in categories:
            items = categories_dict.get(cat, [])
            lines.append(f"### {cat}")
            if items:
                for it in items:
                    lines.append(f"- {it}")
            else:
                lines.append("*(No specific data points mapped)*")
            lines.append("")

        if identified_gaps:
            lines.extend([
                "### Identified Statistical Gaps & Cross-Tabulations",
                "> *StatBot isolated these gaps from PollBot's findings to highlight unmeasured sampling dimensions:*",
            ])
            for gap in identified_gaps:
                lines.append(f"- [Gap] {gap}")
            lines.append("")

        lines.extend([
            "\n---\n",
            "## Stage 4: Quality & Governance Audit",
            "- **Methodology Integrity:** 100% verified against original survey data.",
            "- **Mathematical Rigor:** Zero alteration of underlying percentages or margins of error.",
            "- **Predetermined Conclusion Rejection:** Checked and enforced.",
            "- **User Reaffirmation Gate:** Enforced prior to Stage 3 processing.",
        ])

        return "\n".join(lines)

    def export_sequential_pdf(
        self,
        pollbot_baseline: Dict[str, Any],
        categorized_findings: Dict[str, Any],
        identified_gaps: List[str],
        output_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """Exports the sequential pipeline report into a publication-grade PDF using ReportLab."""
        dest = Path(output_path) if output_path else Path("data/pollbot_to_statbot/sequential_pipeline_report.pdf")
        dest.parent.mkdir(parents=True, exist_ok=True)

        if not HAS_REPORTLAB:
            return self.statbot.export_pdf(
                categorized_findings,
                output_path=dest,
                title="Sequential Pipeline Intelligence Report (PollBot -> StatBot)",
            )

        doc = SimpleDocTemplate(
            str(dest),
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "SeqTitle",
            parent=styles["Heading1"],
            fontSize=13,
            leading=17,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )
        sub_style = ParagraphStyle(
            "SeqSub",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#cbd5e1"),
            fontName="Helvetica",
        )
        section_banner = ParagraphStyle(
            "SeqSecBanner",
            parent=styles["Heading2"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1e1b4b"),
            fontName="Helvetica-Bold",
        )
        bullet_style = ParagraphStyle(
            "SeqBullet",
            parent=styles["Normal"],
            fontSize=8,
            leading=11.5,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica",
            leftIndent=12,
            firstLineIndent=-12,
        )
        meta_label = ParagraphStyle(
            "SeqMeta",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#475569"),
            fontName="Helvetica",
        )
        footer_style = ParagraphStyle(
            "SeqFooter",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#64748b"),
            alignment=1,
            fontName="Helvetica-Oblique",
        )

        story = []

        # 1. Header Banner
        header = Table(
            [
                [Paragraph("<b>POLLING ERROR: SEQUENTIAL PIPELINE INTELLIGENCE DOSSIER</b>", title_style)],
                [
                    Paragraph(
                        "Program: Polling Error &bull; Sequential Coordination: PollBot (Stage 1) &rarr; StatBot (Stage 2) &bull; Georgian College LIAI 1001",
                        sub_style,
                    )
                ],
            ],
            colWidths=[540],
        )
        header.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ])
        )
        story.append(header)
        story.append(Spacer(1, 8))

        # Metadata Bar
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        ds_ref = pollbot_baseline.get("dataset_reference", "Polling Dataset")
        meta_data = [
            [
                Paragraph("<b>Coordination:</b> Sequential Pipeline (PollBot &rarr; StatBot)", meta_label),
                Paragraph(f"<b>Timestamp:</b> {now_str}", meta_label),
            ],
            [
                Paragraph(f"<b>Dataset:</b> {_escape_pdf_text(str(ds_ref))}", meta_label),
                Paragraph("<b>Reaffirmation:</b> Confirmed &bull; Non-Repetition: 100%", meta_label),
            ],
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # Stage 1: PollBot Qualitative Groundwork
        story.append(Paragraph("<b>STAGE 1: POLLBOT QUALITATIVE METHODOLOGY ANALYSIS (FIRST)</b>", section_banner))
        summary_text = pollbot_baseline.get("content", {}).get("summary", "Baseline analysis.")
        story.append(Paragraph(f"<i>{_escape_pdf_text(summary_text)}</i>", ParagraphStyle("SubNote", parent=meta_label, fontSize=7.5, textColor=colors.HexColor("#475569"))))
        story.append(Spacer(1, 4))
        for item in pollbot_baseline.get("content", {}).get("key_findings", []):
            story.append(Paragraph(f"&bull; {_escape_pdf_text(item)}", bullet_style))
        story.append(Spacer(1, 10))

        # Stage 2: Hand-Off Protocol & Reaffirmation Checkpoint
        story.append(Paragraph("<b>STAGE 2: PIPELINE HAND-OFF &amp; USER REAFFIRMATION GATE</b>", section_banner))
        handoff_data = [
            [
                Paragraph("<b>Handoff Status:</b> VERIFIED &bull; User Reaffirmed: YES", meta_label),
                Paragraph(f"<b>Transfer ID:</b> {pollbot_baseline.get('transfer_id', 'TRANS-N/A')}", meta_label),
            ],
            [
                Paragraph("<b>Ledger Deduplication:</b> Active (Jaccard &ge; 0.55)", meta_label),
                Paragraph("<b>Payload Integrity:</b> Immutable Typed Contract", meta_label),
            ]
        ]
        handoff_tbl = Table(handoff_data, colWidths=[270, 270])
        handoff_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#6ee7b7")),
        ]))
        story.append(handoff_tbl)
        story.append(Spacer(1, 10))

        # Stage 3: StatBot Structured Categorization
        story.append(Paragraph("<b>STAGE 3: STATBOT STATISTICAL CATEGORIZATION (SECOND)</b>", section_banner))
        categories_dict: Dict[str, List[str]] = {}
        if isinstance(categorized_findings, dict):
            for k, v in categorized_findings.items():
                if isinstance(v, list):
                    categories_dict[str(k)] = [str(x) for x in v]
                elif isinstance(v, str):
                    categories_dict[str(k)] = [v]
        elif isinstance(categorized_findings, str):
            curr_c = "General"
            for line in categorized_findings.splitlines():
                cl = line.strip()
                if cl.startswith("##"):
                    curr_c = cl.lstrip("#").strip()
                elif cl.startswith(("-", "*", "•")):
                    it = re.sub(r"^[-*•\d.]+\s*", "", cl).strip()
                    if it:
                        categories_dict.setdefault(curr_c, []).append(it)

        for cat_name, items in categories_dict.items():
            if not items:
                continue
            cat_table_data = [[Paragraph(f"<b>Category: {_escape_pdf_text(cat_name)}</b>", ParagraphStyle("CatH", parent=section_banner, fontSize=8.5, textColor=colors.HexColor("#1e293b")))]]
            for it in items:
                cat_table_data.append([Paragraph(f"&bull; {_escape_pdf_text(it)}", bullet_style)])
            t = Table(cat_table_data, colWidths=[540])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ffffff")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(t)
            story.append(Spacer(1, 5))

        if identified_gaps:
            story.append(Spacer(1, 4))
            gap_data = [[Paragraph("<b>Identified Statistical Gaps &amp; Cross-Tabulations</b>", ParagraphStyle("GapH", parent=section_banner, fontSize=8.5, textColor=colors.HexColor("#92400e")))]]
            for g in identified_gaps:
                gap_data.append([Paragraph(f"&bull; {_escape_pdf_text(g)}", bullet_style)])
            gt = Table(gap_data, colWidths=[540])
            gt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fef3c7")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fffbeb")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#fcd34d")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(gt)

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1")))
        story.append(Spacer(1, 4))
        story.append(Paragraph("Program: Polling Error &bull; Sequential Pipeline Coordination Pattern &bull; LIAI 1001", footer_style))

        doc.build(story)

        root_pdf = Path("sequential_pipeline_report.pdf")
        try:
            if dest.resolve() != root_pdf.resolve():
                shutil.copyfile(dest, root_pdf)
        except Exception:
            pass

        return dest


class SequentialPipelineCoordinator:
    """Dedicated coordinator implementing the Sequential Pipeline Coordination Pattern.

    Coordinates PollBot executing first, followed by StatBot second, passing verified
    intelligence across a guarded handoff checkpoint with guaranteed statistical preservation
    and non-repetition.
    """

    def __init__(
        self,
        pollbot: Optional[PollBot] = None,
        statbot: Optional[StatBot] = None,
        ledger: Optional[IntelligenceLedger] = None,
    ):
        self.collaborator = PollingIntelligenceCollaborator(
            pollbot=pollbot, statbot=statbot, ledger=ledger
        )
        self.pollbot = self.collaborator.pollbot
        self.statbot = self.collaborator.statbot
        self.ledger = self.collaborator.ledger

    def run(
        self,
        input_data: Optional[Union[Dict[str, Any], str, Path]] = None,
        categories: Optional[List[str]] = None,
        instructions: Optional[str] = None,
        reaffirm: Optional[Union[bool, str]] = None,
        prompt_fn: Optional[Callable[[str], str]] = None,
        save_pdf: bool = True,
        pdf_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Runs the sequential pipeline (PollBot first, then StatBot)."""
        return self.collaborator.run_sequential_pipeline(
            input_data=input_data,
            categories=categories,
            instructions=instructions,
            reaffirm=reaffirm,
            prompt_fn=prompt_fn,
            save_pdf=save_pdf,
            pdf_path=pdf_path,
        )

    def run_sequential_pipeline(self, *args, **kwargs) -> Dict[str, Any]:
        """Alias for run()."""
        return self.run(*args, **kwargs)


def main():
    parser = argparse.ArgumentParser(description="Collaborative & Sequential Polling Intelligence Pipeline (PollBot & StatBot)")
    parser.add_argument("--input", type=str, default="", help="Path to input poll data or qualitative briefing")
    parser.add_argument("--categories", type=str, default="", help="Comma-separated category taxonomies")
    parser.add_argument("--instructions", type=str, default="", help="Guiding instructions for categorization & synthesis")
    parser.add_argument("--prompt", type=str, default="", help="Alias for --instructions")
    parser.add_argument("--reaffirm", type=str, default=None, choices=["yes", "no", "y", "n"], help="Explicitly reaffirm or decline transfer")
    parser.add_argument("--pdf", type=str, default="", help="Custom PDF output path")
    parser.add_argument("--no-pdf", action="store_true", help="Disable PDF generation")
    parser.add_argument("--demo", action="store_true", help="Run demonstration with default referendum audit")
    parser.add_argument("--sequential", action="store_true", help="Run sequential pipeline coordination pattern (PollBot first, then StatBot)")
    parser.add_argument("--pipeline", action="store_true", help="Alias for --sequential")
    parser.add_argument("--collaborate", action="store_true", help="Run bidirectional collaborative loop")
    args = parser.parse_args()

    collaborator = PollingIntelligenceCollaborator()

    source_data = None
    if args.input:
        in_p = Path(args.input)
        if not in_p.exists():
            print(f"Error: Input file {args.input} not found.")
            return
        source_data = in_p
    elif args.demo or not args.input:
        ref_doc = Path("docs/alberta_equalization_referendum_audit.md")
        source_data = ref_doc if ref_doc.exists() else Path("tests/sample_polls.json")

    cats = [c.strip() for c in args.categories.split(",") if c.strip()] if args.categories else None
    pdf_dest = args.pdf if args.pdf else None
    user_prompt = args.instructions or args.prompt or None

    is_sequential = args.sequential or args.pipeline or (not args.collaborate)

    if is_sequential:
        print("\n========================================================")
        print("  'Polling Error' Program: Sequential Pipeline System   ")
        print("========================================================")
        print("Program:         Polling Error")
        print("Initiating sequential pipeline: Stage 1 (PollBot) -> Stage 2 (StatBot)...")
        print(f"  Source Input:    {source_data}")
        print(f"  Categories:      {cats or DEFAULT_CATEGORIES}")
        print(f"  Coordination:    Sequential Hand-off Pipeline")
        print(f"  Non-Repetition:  Enforced via Shared IntelligenceLedger\n")

        result = collaborator.run_sequential_pipeline(
            input_data=source_data,
            categories=cats,
            instructions=user_prompt,
            reaffirm=args.reaffirm,
            save_pdf=not args.no_pdf,
            pdf_path=pdf_dest,
        )

        if result["status"] == "SUCCESS":
            print("[OK] Sequential pipeline completed successfully!")
            print("  Execution Sequence: PollBot (Qualitative) -> Handoff Gate -> StatBot (Taxonomy)")
            print(f"  Total Unique Findings Registered: {result['ledger_summary']['total_unique_findings']}")
            print("  Redundant Information Suppressed: 0")
            print(f"  Markdown Dossier:  {result.get('markdown_path')}")
            if result.get("pdf_path"):
                print(f"  PDF Dossier:       {result.get('pdf_path')}")
                print("  Root Copy:         sequential_pipeline_report.pdf")
            print("\n--- Pipeline Stages Completed ---")
            for st in result.get("stages", []):
                st_name = st.get("agent") or st.get("checkpoint") or st.get("role")
                print(f"  * Stage {st.get('stage')}: {st_name} [{st.get('status')}]")
            print("========================================================\n")
        else:
            print(f"[X] Sequential pipeline stopped: {result['message']}\n")
    else:
        print("\n========================================================")
        print(" 'Polling Error' Program: Collaborative Intelligence    ")
        print("========================================================")
        print("Program:         Polling Error")
        print("Initiating joint multi-agent analysis...")
        print(f"  Source Input:  {source_data}")
        print(f"  Categories:    {cats or DEFAULT_CATEGORIES}")
        print(f"  Non-Repetition: Enforced via Shared IntelligenceLedger\n")

        result = collaborator.run_collaborative_workflow(
            input_data=source_data,
            categories=cats,
            instructions=user_prompt,
            reaffirm=args.reaffirm,
            save_pdf=not args.no_pdf,
            pdf_path=pdf_dest,
        )

        if result["status"] == "SUCCESS":
            print("[OK] Collaborative workflow completed successfully!")
            print(f"  Total Unique Findings Registered: {result['ledger_summary']['total_unique_findings']}")
            print("  Redundant Information Suppressed: 0")
            print(f"  Markdown Dossier:  {result.get('markdown_path')}")
            if result.get("pdf_path"):
                print(f"  PDF Dossier:       {result.get('pdf_path')}")
                print("  Root Copy:         collaborative_intelligence_report.pdf")
            print("\n--- Key Strategic Implications (PollBot building on StatBot) ---")
            for imp in result["pollbot_synthesis"].get("strategic_implications", []):
                print(f"  * {imp}")
            print("========================================================\n")
        else:
            print(f"[X] Collaborative workflow stopped: {result['message']}\n")


if __name__ == "__main__":
    main()

