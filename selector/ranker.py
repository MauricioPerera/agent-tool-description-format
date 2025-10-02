"""Heuristic ranking utilities for ATDF tool selection."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

from .catalog import ATDFToolRecord, ToolCatalog

_TOKEN_PATTERN = re.compile(r"[\w-]+", re.UNICODE)


@dataclass(order=True)
class RankedTool:
    """Stores the scoring information for a recommended tool."""

    score: float
    record: ATDFToolRecord = field(compare=False)
    reasons: List[str] = field(default_factory=list, compare=False)

    def to_dict(self, include_descriptor: bool = False) -> dict:
        payload = {
            "tool_id": self.record.tool_id,
            "score": round(self.score, 4),
            "description": self.record.description,
            "when_to_use": self.record.when_to_use,
            "languages": self.record.languages,
            "tags": self.record.tags,
            "source": self.record.source,
            "reasons": list(self.reasons),
        }
        if include_descriptor:
            payload["descriptor"] = self.record.raw_descriptor
        return payload


class ToolRanker:
    """Simple heuristic-based ranker for ATDF tools."""

    def __init__(self, catalog: ToolCatalog) -> None:
        self.catalog = catalog

    def rank(
        self,
        query: str,
        top_n: int = 5,
        preferred_language: Optional[str] = None,
        sources: Optional[Sequence[str]] = None,
        tool_ids: Optional[Sequence[str]] = None,
    ) -> List[RankedTool]:
        query = (query or "").strip()
        if not query:
            raise ValueError("Query cannot be empty when ranking tools")

        tokens = self._tokenize(query)
        results: List[RankedTool] = []
        feedback = getattr(self.catalog, 'feedback_summary', lambda: {})()

        for record in self.catalog.list_tools(sources=sources, tool_ids=tool_ids):
            score, reasons = self._score_record(record, tokens, preferred_language)
            key = f"{record.source}::{record.tool_id}"
            stats = feedback.get(key) if feedback else None
            if stats:
                success = int(stats.get('success', 0) or 0)
                error = int(stats.get('error', 0) or 0)
                if success:
                    score += min(success, 3) * 0.5
                    reasons.append(f"historical successes: {success}")
                if error:
                    score -= min(error, 3) * 0.75
                    reasons.append(f"historical errors: {error}")
            if score <= 0:
                continue
            results.append(RankedTool(score=score, record=record, reasons=reasons))

        results.sort(reverse=True)
        if top_n > 0:
            return results[:top_n]
        return results

    # ------------------------------------------------------------------
    # Internal heuristics
    # ------------------------------------------------------------------
    def _score_record(
        self,
        record: ATDFToolRecord,
        tokens: Sequence[str],
        preferred_language: Optional[str],
    ) -> Tuple[float, List[str]]:
        score = 0.0
        reasons: List[str] = []
        searchable_text = " ".join(filter(None, [record.tool_id, record.description, record.when_to_use or ""])).lower()
        tag_text = " ".join(record.tags).lower()

        for token in tokens:
            token_score = 0.0
            if token in record.tool_id.lower():
                token_score += 3.0
                reasons.append(f"token '{token}' matched tool_id")
            if token in searchable_text:
                token_score += 2.0
                reasons.append(f"token '{token}' matched description")
            if token in tag_text:
                token_score += 1.0
                reasons.append(f"token '{token}' matched tag")
            score += token_score

        if preferred_language:
            preferred_language = preferred_language.lower()
            if any(lang.lower().startswith(preferred_language) for lang in record.languages):
                score += 1.5
                reasons.append(f"preferred language '{preferred_language}' available")
            else:
                score -= 1.0
                reasons.append(f"language '{preferred_language}' not available")

        # Minor boost for tools with explicit usage guidance
        if record.when_to_use:
            score += 0.25

        # Reward tags count slightly to prefer well-documented tools
        score += math.log1p(len(record.tags)) * 0.2

        return score, reasons

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [match.group(0).lower() for match in _TOKEN_PATTERN.finditer(text)]


__all__ = ["ToolRanker", "RankedTool"]
