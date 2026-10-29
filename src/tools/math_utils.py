"""Statistical and mathematical helper functions for polling aggregation.

Handles weighted averages, margin of error decomposition, and recency decay.
"""

from __future__ import annotations
import math
from typing import List, Dict, Any


def calculate_theoretical_moe(sample_size: int, confidence: float = 0.95) -> float:
    """Calculates theoretical margin of error (MOE) at 95% confidence level.

    Formula: 1.96 * sqrt(p * (1-p) / n), assuming max variance at p=0.5.

    Args:
        sample_size: Total number of valid respondents.
        confidence: Statistical confidence level (defaults to 0.95).

    Returns:
        Margin of error as a percentage (e.g. 2.8 for +/-2.8%).
    """
    if sample_size <= 0:
        return 0.0
    z_score = 1.96 if confidence == 0.95 else 2.576
    moe = z_score * math.sqrt(0.25 / sample_size) * 100.0
    return round(moe, 2)


def compute_weighted_average(values: List[float], weights: List[float]) -> float:
    """Computes weighted arithmetic mean.

    Args:
        values: List of candidate share values.
        weights: List of corresponding statistical weights.

    Returns:
        Weighted mean rounded to two decimal places.
    """
    if not values or not weights or len(values) != len(weights):
        return 0.0
    total_weight = sum(weights)
    if total_weight == 0.0:
        return 0.0
    weighted_sum = sum(v * w for v, w in zip(values, weights))
    return round(weighted_sum / total_weight, 2)


def calculate_divergence(actual_share: float, consensus_share: float) -> float:
    """Calculates absolute divergence between an individual poll and the consensus signal.

    Args:
        actual_share: Candidate percentage in a specific poll.
        consensus_share: Candidate weighted consensus percentage.

    Returns:
        Absolute percentage difference.
    """
    return round(abs(actual_share - consensus_share), 2)
