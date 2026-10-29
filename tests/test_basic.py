"""Basic unit and integration tests for AI Polling Intelligence system.

Supports both standard library `unittest` and `pytest`.
"""

from __future__ import annotations
import json
import unittest
import tempfile
from pathlib import Path

from src.tools.math_utils import calculate_theoretical_moe, compute_weighted_average, calculate_divergence
from src.agents.normalizer import NormalizerAgent
from src.agents.modeler import ModelerAgent
from src.agents.explainer import ExplainerAgent
from src.orchestrator.pipeline import PollingIntelligencePipeline, DEFAULT_POLLS


class TestPollingIntelligenceSystem(unittest.TestCase):
    """Test suite verifying agent logic, statistical calculations, and pipeline coordination."""

    def test_calculate_theoretical_moe(self):
        """Verify margin of error formula produces expected standard results."""
        moe = calculate_theoretical_moe(1000)
        self.assertTrue(3.0 <= moe <= 3.2)
        self.assertEqual(calculate_theoretical_moe(0), 0.0)

    def test_weighted_average(self):
        """Verify weighted average calculation."""
        values = [50.0, 40.0]
        weights = [3.0, 1.0]
        avg = compute_weighted_average(values, weights)
        self.assertEqual(avg, 47.5)

    def test_divergence(self):
        """Verify divergence calculation."""
        self.assertEqual(calculate_divergence(52.0, 48.0), 4.0)
        self.assertEqual(calculate_divergence(45.0, 48.5), 3.5)

    def test_normalizer_agent(self):
        """Verify NormalizerAgent applies proper weighting factors."""
        agent = NormalizerAgent()
        normalized = agent.process(DEFAULT_POLLS)
        self.assertEqual(len(normalized), 3)
        self.assertEqual(normalized[0]["status"], "NORMALIZED")
        self.assertGreater(normalized[0]["composite_weight"], 0)

    def test_modeler_agent_outlier_detection(self):
        """Verify ModelerAgent identifies outlier divergence."""
        normalizer = NormalizerAgent()
        modeler = ModelerAgent(outlier_threshold_percent=3.5)
        normalized = normalizer.process(DEFAULT_POLLS)
        result = modeler.model_consensus(normalized)

        self.assertEqual(result["total_polls"], 3)
        self.assertGreater(result["consensus_a"], 0)
        self.assertGreater(result["consensus_b"], 0)
        self.assertTrue(result["has_outlier"])
        self.assertGreaterEqual(len(result["outliers"]), 1)

    def test_explainer_agent_triggers_checkpoint(self):
        """Verify ExplainerAgent flags human checkpoint on outlier."""
        normalizer = NormalizerAgent()
        modeler = ModelerAgent(outlier_threshold_percent=3.5)
        explainer = ExplainerAgent()

        normalized = normalizer.process(DEFAULT_POLLS)
        model_result = modeler.model_consensus(normalized)
        brief = explainer.generate_brief(model_result, normalized)

        self.assertTrue(brief["requires_human_checkpoint"])
        self.assertGreater(len(brief["causal_hypotheses"]), 0)
        self.assertIn("Executive Polling Intelligence Brief", brief["markdown_brief"])

    def test_full_pipeline_run(self):
        """Verify end-to-end pipeline execution and evidence generation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            pipeline = PollingIntelligencePipeline(interactive=False, evidence_dir=tmp_dir)
            run_result = pipeline.run(DEFAULT_POLLS)

            self.assertEqual(run_result["status"], "SUCCESS")
            brief_file = Path(tmp_dir) / "output_brief.md"
            self.assertTrue(brief_file.exists())
            content = brief_file.read_text(encoding="utf-8")
            self.assertIn("Consensus Signal", content)
            self.assertIn("Human Checkpoint Verification", content)


if __name__ == "__main__":
    unittest.main()
