"""Statistical tools and calculation utilities."""

from src.tools.math_utils import (
    calculate_theoretical_moe,
    compute_weighted_average,
    calculate_divergence,
)
from src.tools.search_tool import SerpSearchTool
from src.tools.ledger import IntelligenceLedger

__all__ = [
    "calculate_theoretical_moe",
    "compute_weighted_average",
    "calculate_divergence",
    "SerpSearchTool",
    "IntelligenceLedger",
    "PollingErrorPrompter",
]


def __getattr__(name: str):
    if name == "PollingErrorPrompter":
        from src.tools.prompter import PollingErrorPrompter
        return PollingErrorPrompter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
