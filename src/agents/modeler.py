"""Statistical Modeling Agent.

Computes consensus signals, detects pollster variance, and flags statistical outliers.
"""

from __future__ import annotations
from typing import List, Dict, Any
from src.tools.math_utils import compute_weighted_average, calculate_divergence


class ModelerAgent:
    """Agent responsible for Bayesian consensus synthesis and outlier detection."""

    def __init__(self, outlier_threshold_percent: float = 3.5):
        self.outlier_threshold = outlier_threshold_percent

    def model_consensus(self, normalized_polls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates aggregate candidate consensus and detects outliers.

        Args:
            normalized_polls: List of normalized poll dictionaries.

        Returns:
            Dictionary containing consensus signal, error metrics, and flagged outliers.
        """
        if not normalized_polls:
            return {
                "consensus_a": 0.0,
                "consensus_b": 0.0,
                "undecided": 0.0,
                "total_polls": 0,
                "outliers": [],
                "has_outlier": False,
            }

        shares_a = [p["candidate_a_share"] for p in normalized_polls]
        shares_b = [p["candidate_b_share"] for p in normalized_polls]
        shares_undecided = [p["undecided_share"] for p in normalized_polls]
        weights = [p["composite_weight"] for p in normalized_polls]

        consensus_a = compute_weighted_average(shares_a, weights)
        consensus_b = compute_weighted_average(shares_b, weights)
        consensus_undecided = compute_weighted_average(shares_undecided, weights)

        outliers = []
        for poll in normalized_polls:
            div_a = calculate_divergence(poll["candidate_a_share"], consensus_a)
            div_b = calculate_divergence(poll["candidate_b_share"], consensus_b)
            max_div = max(div_a, div_b)

            if max_div >= self.outlier_threshold:
                outliers.append({
                    "poll_id": poll["poll_id"],
                    "pollster": poll["pollster"],
                    "divergence": max_div,
                    "candidate_a": poll["candidate_a_share"],
                    "candidate_b": poll["candidate_b_share"],
                    "sample_frame": poll["sample_frame"],
                    "mode": poll["mode"],
                })

        return {
            "consensus_a": consensus_a,
            "consensus_b": consensus_b,
            "consensus_undecided": consensus_undecided,
            "margin_spread": round(abs(consensus_a - consensus_b), 2),
            "leader": "Candidate A" if consensus_a > consensus_b else ("Candidate B" if consensus_b > consensus_a else "Tied"),
            "total_polls": len(normalized_polls),
            "outliers": outliers,
            "has_outlier": len(outliers) > 0,
        }
