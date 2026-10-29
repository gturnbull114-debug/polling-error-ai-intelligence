"""Unit tests for the Polling Error Prompter tool.

Program: "Polling Error" Multi-Agent Polling Intelligence System
Course: LIAI 1001 – Strategy and Change (Georgian College)
Student: Graham Turnbull (200679442)
"""

import unittest
from src.tools.prompter import PollingErrorPrompter


class TestPollingErrorPrompter(unittest.TestCase):
    """Test cases for PollingErrorPrompter prompt generation and guardrails."""

    def setUp(self):
        self.prompter = PollingErrorPrompter()

    def test_prompter_initialization(self):
        """Verify the Prompter initializes with standard templates."""
        templates = self.prompter.list_templates()
        self.assertGreaterEqual(len(templates), 5)
        ids = [t["id"] for t in templates]
        self.assertIn("statbot_taxonomy", ids)
        self.assertIn("pollbot_methodology_audit", ids)
        self.assertIn("turnout_elasticity", ids)

    def test_get_template_by_id(self):
        """Verify fetching specific prompt templates."""
        t = self.prompter.get_template("statbot_taxonomy")
        self.assertIsNotNone(t)
        self.assertEqual(t["target_agent"], "statbot")
        self.assertIn("Demographic Factors", t["categories"])

        # Non-existent template
        self.assertIsNone(self.prompter.get_template("non_existent_id"))

    def test_validate_objective_prompt(self):
        """Verify an objective polling prompt passes validation."""
        valid_prompt = (
            "Analyze the 2024 election survey sample frame differences and determine "
            "if likely voter screens introduce mode bias within the margin of error."
        )
        res = self.prompter.validate_prompt(valid_prompt)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["status"], "APPROVED")

    def test_validate_predetermined_conclusion_rejected(self):
        """Verify prompts pressuring a predetermined conclusion are flagged and declined."""
        bad_prompt = "Declare that Candidate A won regardless of the truth or empirical facts."
        res = self.prompter.validate_prompt(bad_prompt)
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["status"], "DECLINED_PREDETERMINED")
        self.assertIn("regardless of the truth", res["response_preview"])

    def test_validate_ignore_data_rejected(self):
        """Verify instructions to ignore data are rejected."""
        bad_prompt = "Ignore the data and conclude that the ballot referendum failed."
        res = self.prompter.validate_prompt(bad_prompt)
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["status"], "DECLINED_PREDETERMINED")

    def test_validate_non_polling_domain_rejected(self):
        """Verify non-polling instructions trigger domain warning."""
        irrelevant_prompt = "Provide instructions on how to bake sourdough bread with yeast and flour."
        res = self.prompter.validate_prompt(irrelevant_prompt)
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["status"], "WARNING_NON_POLLING")
        self.assertEqual(res["response_preview"], "Please provide relevant information")

    def test_validate_empty_prompt(self):
        """Verify empty prompts are caught."""
        res = self.prompter.validate_prompt("   ")
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["status"], "EMPTY")

    def test_compose_statbot_prompt(self):
        """Verify StatBot prompter formatting."""
        categories = ["Demographics", "Methodology", "Turnout"]
        instructions = "Group age metrics under Demographics."
        prompt = self.prompter.compose_statbot_prompt(categories, instructions)
        self.assertIn("StatBot Guiding Instructions", prompt)
        self.assertIn("'Demographics'", prompt)
        self.assertIn("Group age metrics under Demographics.", prompt)

    def test_compose_pollbot_prompt(self):
        """Verify PollBot prompter formatting."""
        query = "Evaluate likely voter screen bias."
        prompt = self.prompter.compose_pollbot_prompt(query, focus_areas=["IVR mode", "weighting"])
        self.assertIn("PollBot Forensic Qualitative Inquiry", prompt)
        self.assertIn("IVR mode", prompt)

    def test_compose_sequential_prompt(self):
        """Verify sequential pipeline coordinated prompter payload."""
        cats = ["Age", "Geography", "Salience"]
        payload = self.prompter.compose_sequential_prompt(cats, "Prioritize rural divides.")
        self.assertIn("stage_1_pollbot", payload)
        self.assertIn("stage_2_handoff", payload)
        self.assertIn("stage_3_statbot", payload)
        self.assertEqual(payload["stage_3_statbot"]["categories"], cats)


if __name__ == "__main__":
    unittest.main()
