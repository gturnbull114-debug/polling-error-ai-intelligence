"""Causal Explanation & Audit Agent.

Decomposes margin of error, generates causal hypotheses, and creates an audit brief.
Can collaborate with PollBot (Anthropic Claude) for deep qualitative reasoning.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from src.agents.pollbot import PollBot


class ExplainerAgent:
    """Agent responsible for explaining divergence, non-sampling errors, and drafting briefings."""

    def __init__(self, name: str = "ExplainerAgent", use_ai: bool = True):
        self.name = name
        self.use_ai = use_ai
        self.pollbot = PollBot() if use_ai else None

    def generate_brief(
        self,
        model_results: Dict[str, Any],
        normalized_polls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates a structured qualitative analysis and audit ledger.

        Args:
            model_results: Output from ModelerAgent.
            normalized_polls: Input polls used in calculation.

        Returns:
            Dictionary containing causal audit ledger and formatted Markdown brief.
        """
        has_outlier = model_results.get("has_outlier", False)
        outliers = model_results.get("outliers", [])
        consensus_a = model_results.get("consensus_a", 0.0)
        consensus_b = model_results.get("consensus_b", 0.0)
        spread = model_results.get("margin_spread", 0.0)
        leader = model_results.get("leader", "Tied")

        causal_points = []
        ai_narrative = ""

        if has_outlier:
            # Deterministic baseline points
            for o in outliers:
                reason = (
                    f"Outlier Poll [{o['poll_id']} - {o['pollster']}] shows divergence of {o['divergence']}%. "
                    f"Likely causal driver: Sample frame ({o['sample_frame']}) and collection mode ({o['mode']}) "
                    "introduce non-response skews relative to likely-voter live phone benchmarks."
                )
                causal_points.append(reason)

            # Optional AI enhancement via PollBot (Anthropic Claude)
            if self.pollbot and self.pollbot.is_connected:
                try:
                    ai_narrative = self.pollbot.explain_outliers(
                        outliers=outliers,
                        consensus_a=consensus_a,
                        consensus_b=consensus_b,
                    )
                except Exception:
                    ai_narrative = ""
        else:
            causal_points.append(
                "High methodological cohesion observed across pollsters; observed variance falls comfortably within statistical MOE."
            )

        # Markdown formatted briefing document
        brief_parts = [
            "# Executive Polling Intelligence Brief",
            "",
            "## 1. Consensus Signal",
            f"- **Candidate A:** {consensus_a}%",
            f"- **Candidate B:** {consensus_b}%",
            f"- **Consensus Spread:** {spread}% ({leader} leading)",
            f"- **Total Polls Evaluated:** {model_results.get('total_polls', 0)}",
            "",
            "## 2. Plausible Error & Causal Explanation Ledger",
            "\n".join(["- " + pt for pt in causal_points]),
        ]

        if ai_narrative:
            brief_parts.extend([
                "",
                "### PollBot Qualitative Assessment (Anthropic Claude)",
                ai_narrative,
            ])

        brief_parts.extend([
            "",
            "## 3. Margin of Error & Methodological Audit",
            "- **Reported Variance:** Polls in this window range from likely voter screens to general adult panels.",
            f"- **Outliers Detected:** {len(outliers)} flagged poll(s) exceeded the 3.5% divergence threshold.",
            f"- **Audit Recommendation:** {'Proceed with human analyst sign-off before public dissemination.' if has_outlier else 'Safe for automated baseline reporting.'}",
        ])

        markdown_content = "\n".join(brief_parts) + "\n"

        return {
            "causal_hypotheses": causal_points,
            "ai_narrative": ai_narrative,
            "markdown_brief": markdown_content,
            "requires_human_checkpoint": has_outlier,
            "audit_status": "FLAGGED_FOR_HUMAN_REVIEW" if has_outlier else "APPROVED_AUTOMATED",
        }
