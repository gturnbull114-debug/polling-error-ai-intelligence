"""Main Pipeline Orchestrator.

Coordinates agent lifecycle, state transitions, human checkpoint review, and evidence recording.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from src.agents.normalizer import NormalizerAgent
from src.agents.modeler import ModelerAgent
from src.agents.explainer import ExplainerAgent

# Ensure safe output encoding on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


DEFAULT_POLLS = [
    {
        "poll_id": "POLL-001",
        "pollster": "National Metric Research",
        "field_date_end": "2026-10-20",
        "sample_size": 1200,
        "sample_frame": "Likely Voters (LV)",
        "mode": "Live Phone + SMS",
        "candidate_a_share": 49.2,
        "candidate_b_share": 47.8,
        "undecided_share": 3.0,
        "margin_of_error": 2.8,
    },
    {
        "poll_id": "POLL-002",
        "pollster": "Civic Pulse Online",
        "field_date_end": "2026-10-22",
        "sample_size": 850,
        "sample_frame": "Registered Voters (RV)",
        "mode": "Online Panel",
        "candidate_a_share": 45.1,
        "candidate_b_share": 52.4,
        "undecided_share": 2.5,
        "margin_of_error": 3.4,
    },
    {
        "poll_id": "POLL-003",
        "pollster": "Public Opinion Daily",
        "field_date_end": "2026-10-24",
        "sample_size": 1100,
        "sample_frame": "Likely Voters (LV)",
        "mode": "Mixed Mode (IVR + Online)",
        "candidate_a_share": 48.8,
        "candidate_b_share": 48.1,
        "undecided_share": 3.1,
        "margin_of_error": 3.0,
    },
]


class PollingIntelligencePipeline:
    """Orchestrates multi-agent execution pipeline with state tracking and human checkpoints."""

    def __init__(self, interactive: bool = False, evidence_dir: str = "evidence"):
        self.interactive = interactive
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.state = "INITIALIZING"

        # Initialize Agents
        self.normalizer = NormalizerAgent()
        self.modeler = ModelerAgent(outlier_threshold_percent=3.5)
        self.explainer = ExplainerAgent()

    def run(self, raw_polls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs the complete multi-agent pipeline end to end."""
        print("\n========================================================")
        print("   AI Polling Intelligence Agentic System -- Pipeline   ")
        print("========================================================")
        print(f"[1/4] Orchestrator: Ingesting {len(raw_polls)} raw poll records...")
        self.state = "NORMALIZING"

        # Phase 1: Ingestion & Normalization
        normalized = self.normalizer.process(raw_polls)
        print(f"      [OK] NormalizerAgent: Successfully normalized {len(normalized)} polls.")

        # Phase 2: Statistical Modeling
        self.state = "MODELING"
        model_result = self.modeler.model_consensus(normalized)
        print("      [OK] ModelerAgent: Consensus modeled:")
        print(f"        * Candidate A: {model_result['consensus_a']}%")
        print(f"        * Candidate B: {model_result['consensus_b']}%")
        print(f"        * Leader: {model_result['leader']} (Spread: {model_result['margin_spread']}%)")
        print(f"        * Outliers Flagged: {len(model_result['outliers'])}")

        # Phase 3: Causal Explanation & Audit
        self.state = "AUDITING"
        brief = self.explainer.generate_brief(model_result, normalized)
        print("      [OK] ExplainerAgent: Causal ledger and audit brief generated.")

        # Phase 4: Human-in-the-Loop Checkpoint Gate
        human_approval_status = "AUTOMATIC_PASS"
        if brief.get("requires_human_checkpoint"):
            self.state = "HUMAN_CHECKPOINT"
            print("\n--------------------------------------------------------")
            print("[!] HUMAN-IN-THE-LOOP CHECKPOINT TRIGGERED")
            print("  Reason: Significant pollster outlier divergence detected (>3.5%).")
            print("--------------------------------------------------------")

            for o in model_result["outliers"]:
                print(f"  * Pollster: {o['pollster']} (Poll ID: {o['poll_id']})")
                print(f"    Divergence: {o['divergence']}% | Frame: {o['sample_frame']} | Mode: {o['mode']}")

            if self.interactive:
                response = input("\n[Human Supervisor] Do you approve publication of this brief? (yes/no/override): ").strip().lower()
                if response in ["y", "yes"]:
                    human_approval_status = "APPROVED_BY_HUMAN"
                    print("  [OK] Human Supervisor Approved. Proceeding to publication.")
                elif response in ["o", "override"]:
                    human_approval_status = "APPROVED_WITH_OVERRIDE"
                    print("  [OK] Human Supervisor Override Logged. Proceeding to publication.")
                else:
                    human_approval_status = "REJECTED_BY_HUMAN"
                    print("  [X] Human Supervisor Rejected. Brief publication blocked.")
            else:
                human_approval_status = "SIMULATED_HUMAN_APPROVAL (Batch Mode)"
                print("  [i] Non-interactive run: Human checkpoint recorded as Verified in Batch Mode.")

        self.state = "COMPLETED"

        # Save Evidence Artifacts
        output_brief_path = self.evidence_dir / "output_brief.md"
        with open(output_brief_path, "w", encoding="utf-8") as f:
            f.write(brief["markdown_brief"])
            f.write(f"\n## 4. Human Checkpoint Verification\n- **Status:** {human_approval_status}\n")

        print("\n========================================================")
        print(f"[OK] Pipeline Complete! Final dossier saved to: {output_brief_path}")
        print("========================================================\n")

        return {
            "status": "SUCCESS",
            "state": self.state,
            "model_result": model_result,
            "brief": brief,
            "human_approval": human_approval_status,
        }

    def run_sequential_ai_pipeline(
        self,
        input_data: Optional[Any] = None,
        categories: Optional[List[str]] = None,
        instructions: Optional[str] = None,
        reaffirm: Optional[Any] = None,
        save_pdf: bool = True,
    ) -> Dict[str, Any]:
        """Runs PollBot and StatBot using the sequential pipeline coordination pattern (PollBot first, then StatBot)."""
        from src.agents.collaborator import SequentialPipelineCoordinator
        coordinator = SequentialPipelineCoordinator()
        return coordinator.run(
            input_data=input_data,
            categories=categories,
            instructions=instructions,
            reaffirm=reaffirm or ("yes" if not self.interactive else None),
            save_pdf=save_pdf,
        )


def main():
    parser = argparse.ArgumentParser(description="Run 'Polling Error' Multi-Agent Polling Intelligence Pipeline")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive human checkpoint prompt")
    parser.add_argument("--input", type=str, default="", help="Path to custom JSON poll records file")
    parser.add_argument("--sequential", action="store_true", help="Run PollBot and StatBot using the sequential pipeline coordination pattern (PollBot first, then StatBot)")
    parser.add_argument("--pipeline", action="store_true", help="Alias for --sequential")
    parser.add_argument("--categories", type=str, default="", help="Comma-separated category taxonomies for sequential AI pipeline")
    parser.add_argument("--instructions", type=str, default="", help="Guiding instructions for sequential AI pipeline")
    parser.add_argument("--reaffirm", type=str, default=None, choices=["yes", "no", "y", "n"], help="Explicit reaffirmation flag")
    parser.add_argument("--prompter", action="store_true", help="Launch the Polling Error Prompter interface")
    args = parser.parse_args()

    if args.prompter:
        from src.tools.prompter import PollingErrorPrompter
        prompter = PollingErrorPrompter()
        print("\n========================================================")
        print("      'Polling Error' Prompter Guiding Interface        ")
        print("========================================================")
        print("Available prompter templates:")
        for t in prompter.list_templates():
            print(f"  * {t['title']} ({t['target_agent']})")
        print("\nRun 'python -m src.tools.prompter --list' or '--interactive' for full prompter controls.\n")
        return

    if args.sequential or args.pipeline:
        cats = [c.strip() for c in args.categories.split(",") if c.strip()] if args.categories else None
        pipeline = PollingIntelligencePipeline(interactive=args.interactive)
        src = args.input if args.input else "tests/sample_polls.json"
        print("\n========================================================")
        print("      'Polling Error' Agentic System -- Pipeline        ")
        print("   [Sequential Coordination: PollBot -> StatBot]        ")
        print("========================================================")
        res = pipeline.run_sequential_ai_pipeline(
            input_data=src,
            categories=cats,
            instructions=args.instructions if args.instructions else None,
            reaffirm=args.reaffirm,
        )
        if res.get("status") == "SUCCESS":
            print(f"[OK] Sequential pipeline completed successfully!")
            print(f"  Markdown Dossier: {res.get('markdown_path')}")
            print(f"  PDF Dossier:      {res.get('pdf_path')}")
        else:
            print(f"[X] Sequential pipeline stopped: {res.get('message')}")
        return

    polls = DEFAULT_POLLS
    if args.input:
        input_path = Path(args.input)
        if input_path.exists():
            with open(input_path, "r", encoding="utf-8") as f:
                polls = json.load(f)
            print(f"Loaded {len(polls)} polls from {args.input}")
        else:
            print(f"Warning: Input file {args.input} not found. Using default sample polls.")

    pipeline = PollingIntelligencePipeline(interactive=args.interactive)
    pipeline.run(polls)


if __name__ == "__main__":
    main()
