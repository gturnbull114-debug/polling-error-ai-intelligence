"""Collaborative Intelligence Ledger & Deduplication Engine.

Course: LIAI 1001 – Strategy and Change (Georgian College)
Student: Graham Turnbull (200679442)

Provides shared fact tracking, novelty verification, and semantic deduplication
to ensure PollBot and StatBot build off each other's work without repeating information.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional, Set, Tuple


def _normalize_tokens(text: str) -> Set[str]:
    """Extracts normalized alphanumeric word tokens from text, ignoring stopwords."""
    stopwords = {
        "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with",
        "by", "is", "was", "are", "were", "be", "been", "that", "this", "it", "as",
        "from", "at", "which", "showed", "recorded", "reached", "noted", "survey"
    }
    words = re.findall(r"\b[a-zA-Z0-9%+-]+\b", text.lower())
    return {w for w in words if len(w) > 1 and w not in stopwords}


def _extract_numbers_and_percents(text: str) -> Set[str]:
    """Extracts all numerical and percentage quantities mentioned in a finding."""
    return set(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))


class IntelligenceLedger:
    """Maintains a persistent ledger of established findings across agents to prevent repetition."""

    def __init__(self, name: str = "SharedPollingLedger"):
        self.name = name
        self.entries: List[Dict[str, Any]] = []
        self._seen_signatures: Set[str] = set()

    def _compute_signature(self, text: str) -> str:
        """Computes a canonical signature based on key numbers and tokens."""
        tokens = sorted(_normalize_tokens(text))
        nums = sorted(_extract_numbers_and_percents(text))
        num_str = "_".join(nums)
        token_sub = "_".join(tokens[:8])
        return f"nums:{num_str}|toks:{token_sub}"

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculates Jaccard token similarity with weight given to shared numerical figures."""
        toks_a = _normalize_tokens(text_a)
        toks_b = _normalize_tokens(text_b)
        if not toks_a or not toks_b:
            return 0.0

        intersection = toks_a.intersection(toks_b)
        union = toks_a.union(toks_b)
        jaccard = len(intersection) / len(union)

        # Numerical check: if both have numbers and all numbers match, boost similarity
        nums_a = _extract_numbers_and_percents(text_a)
        nums_b = _extract_numbers_and_percents(text_b)
        if nums_a and nums_b:
            num_overlap = len(nums_a.intersection(nums_b)) / max(len(nums_a), len(nums_b))
            if num_overlap >= 0.75 and jaccard >= 0.35:
                return max(jaccard, 0.75)

        return jaccard

    def is_duplicate(self, candidate: str, threshold: float = 0.55) -> bool:
        """Determines whether a candidate finding substantially repeats an already recorded finding."""
        if not candidate or not candidate.strip():
            return True

        clean = candidate.strip()
        sig = self._compute_signature(clean)
        if sig in self._seen_signatures:
            return True

        for entry in self.entries:
            existing_text = entry["text"]
            # Exact or near-exact match
            if clean.lower() == existing_text.lower():
                return True
            # High token/metric similarity
            sim = self.calculate_similarity(clean, existing_text)
            if sim >= threshold:
                return True

        return False

    def register(
        self,
        agent: str,
        finding: str,
        category: Optional[str] = None,
        builds_on: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Registers a finding into the ledger if it is novel.

        Returns:
            True if novel and registered; False if duplicate / repeated.
        """
        if self.is_duplicate(finding):
            return False

        clean = finding.strip()
        sig = self._compute_signature(clean)
        self._seen_signatures.add(sig)

        entry = {
            "id": len(self.entries) + 1,
            "agent": agent,
            "text": clean,
            "category": category,
            "builds_on": builds_on,
            "metadata": metadata or {},
        }
        self.entries.append(entry)
        return True

    def filter_novel(
        self,
        agent: str,
        candidates: List[str],
        category: Optional[str] = None,
        builds_on: Optional[str] = None,
        auto_register: bool = True,
    ) -> List[str]:
        """Filters a list of candidate strings, returning only novel (non-repeating) items."""
        novel_items: List[str] = []
        for cand in candidates:
            if not self.is_duplicate(cand):
                novel_items.append(cand.strip())
                if auto_register:
                    self.register(agent, cand, category=category, builds_on=builds_on)
        return novel_items

    def get_findings_by_agent(self, agent: str) -> List[Dict[str, Any]]:
        """Returns all recorded findings contributed by a specific agent."""
        return [e for e in self.entries if e["agent"].lower() == agent.lower()]

    def get_all_findings(self) -> List[Dict[str, Any]]:
        """Returns all recorded findings in chronological registration order."""
        return list(self.entries)

    def count(self) -> int:
        """Returns the total number of unique registered findings."""
        return len(self.entries)

    def clear(self) -> None:
        """Resets the ledger."""
        self.entries = []
        self._seen_signatures.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the ledger for audit trails or JSON storage."""
        return {
            "ledger_name": self.name,
            "total_unique_findings": len(self.entries),
            "findings": self.entries,
        }
