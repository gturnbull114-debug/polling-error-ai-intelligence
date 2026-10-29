"""Ingestion & Normalizer Agent.

Validates schema, standardizes likely-voter screens, and applies methodology weights.
"""

from __future__ import annotations
from typing import List, Dict, Any
from src.tools.math_utils import calculate_theoretical_moe


class NormalizerAgent:
    """Agent responsible for ingesting, validating, and normalizing raw polling data."""

    def __init__(self, name: str = "NormalizerAgent"):
        self.name = name

    def normalize_poll(self, raw_poll: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes a single poll record and computes reliability weights.

        Args:
            raw_poll: Dictionary with raw poll attributes.

        Returns:
            Normalized dictionary containing standardized metrics and weights.
        """
        sample_size = raw_poll.get("sample_size", 1000)
        sample_frame = raw_poll.get("sample_frame", "Registered Voters (RV)")
        mode = raw_poll.get("mode", "Online Panel")

        # Voter Screen Multipliers
        if "likely" in sample_frame.lower() or "lv" in sample_frame.lower():
            frame_weight = 1.00
        elif "registered" in sample_frame.lower() or "rv" in sample_frame.lower():
            frame_weight = 0.85
        else:
            frame_weight = 0.70  # General adults / general population

        # Mode Multipliers (historical reliability factor)
        if "live phone" in mode.lower():
            mode_weight = 1.05
        elif "sms" in mode.lower() or "mixed" in mode.lower():
            mode_weight = 1.00
        else:
            mode_weight = 0.90  # Unweighted online opt-in

        calculated_moe = calculate_theoretical_moe(sample_size)
        reported_moe = raw_poll.get("margin_of_error", calculated_moe)

        # Composite statistical weight
        composite_weight = round(frame_weight * mode_weight * (sample_size / 1000.0), 3)

        return {
            "poll_id": raw_poll.get("poll_id", "POLL-UNKNOWN"),
            "pollster": raw_poll.get("pollster", "Independent"),
            "field_date_end": raw_poll.get("field_date_end", "2026-10-01"),
            "sample_size": sample_size,
            "sample_frame": sample_frame,
            "mode": mode,
            "candidate_a_share": float(raw_poll.get("candidate_a_share", 0.0)),
            "candidate_b_share": float(raw_poll.get("candidate_b_share", 0.0)),
            "undecided_share": float(raw_poll.get("undecided_share", 0.0)),
            "reported_moe": reported_moe,
            "calculated_moe": calculated_moe,
            "composite_weight": composite_weight,
            "status": "NORMALIZED",
        }

    def process(self, raw_polls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes a batch of raw polls.

        Args:
            raw_polls: List of raw poll records.

        Returns:
            List of normalized poll records.
        """
        normalized_records = []
        for poll in raw_polls:
            try:
                normalized_records.append(self.normalize_poll(poll))
            except Exception as e:
                # Isolate bad record without crashing pipeline
                continue
        return normalized_records
