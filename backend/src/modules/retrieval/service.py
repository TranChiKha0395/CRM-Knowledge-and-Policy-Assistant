"""Pre-filtered hybrid Vietnamese retrieval service (ANS 02, VN 01)."""

import re

from src.config import settings
from src.modules.knowledge.schemas import PassageSummary
from src.modules.retrieval.models import VIETNAMESE_CRM_SYNONYMS
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.contracts import HybridQuerySpec
from src.shared.enums import PolicyLifecycleStatus


class RetrievalService:
    """Filters by permission/lifecycle before ranking and preserves Vietnamese negations."""

    def normalize_query_vi(self, query: str) -> tuple[str, list[str]]:
        """Normalize whitespace while preserving digits, negations, and CRM synonyms."""
        cleaned = re.sub(r"\s+", " ", query.strip())
        tokens = re.findall(r"[\w]+", cleaned.lower())
        expanded: list[str] = []
        for token in tokens:
            if token in VIETNAMESE_CRM_SYNONYMS:
                expanded.extend(VIETNAMESE_CRM_SYNONYMS[token])
        return cleaned, list(dict.fromkeys(expanded))

    def prefilter_passages(
        self,
        user: AuthenticatedUser,
        candidates: list[PassageSummary],
        *,
        allow_historical: bool = False,
        allow_future_preview: bool = False,
        top_k: int | None = None,
    ) -> list[PassageSummary]:
        """Enforce RBAC, attachment completeness, and status filtering BEFORE ranking."""
        limit = min(top_k or settings.ANSWER_MAX_PASSAGES, settings.ANSWER_MAX_PASSAGES)
        filtered: list[PassageSummary] = []

        for p in candidates:
            if not check_policy_audience(user, p.audience):
                continue
            if not p.has_essential_attachments:
                continue
            if len(p.content) > settings.PASSAGE_MAX_CHARS:
                continue
            if p.status in {
                PolicyLifecycleStatus.DRAFT,
                PolicyLifecycleStatus.OWNER_REVIEWED,
                PolicyLifecycleStatus.APPROVED,
                PolicyLifecycleStatus.WITHDRAWN,
                PolicyLifecycleStatus.QUARANTINED,
                PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
            }:
                continue
            if p.status == PolicyLifecycleStatus.SCHEDULED and not allow_future_preview:
                continue
            if p.status == PolicyLifecycleStatus.SUPERSEDED and not allow_historical:
                continue
            filtered.append(p)
            if len(filtered) >= limit:
                break

        return filtered

    def compute_rrf_score(
        self,
        vector_rank: int | None,
        fts_rank: int | None,
        trgm_rank: int | None = None,
        *,
        k: int = 60,
    ) -> float:
        """Compute deterministic Reciprocal Rank Fusion score across retrieval signals."""
        if k <= 0:
            raise ValueError("RRF smoothing constant k must be positive.")

        score = 0.0
        for rank in (vector_rank, fts_rank, trgm_rank):
            if rank is None:
                continue
            if rank < 1:
                raise ValueError("RRF rank must be >= 1 when provided.")
            score += 1.0 / (k + rank)
        return score

    async def search_hybrid(
        self,
        user: AuthenticatedUser,
        spec: HybridQuerySpec,
    ) -> list[PassageSummary]:
        """Run pre-filtered Vietnamese hybrid retrieval (RRF scaffold for Gate G1)."""
        _normalized, _expanded = self.normalize_query_vi(spec.query)
        # TODO(G1): Query PostgreSQL pgvector + FTS + pg_trgm candidates matching
        # spec.applicable_version_ids and rank via compute_rrf_score after prefilter_passages.
        return self.prefilter_passages(
            user,
            [],
            allow_historical=spec.allow_historical,
            allow_future_preview=spec.allow_future_preview,
            top_k=spec.top_k,
        )

    async def fetch_authoritative_passages(
        self,
        user: AuthenticatedUser,
        passage_ids: list[str],
    ) -> dict[str, PassageSummary]:
        """Re-fetch live authoritative passage state for Layer 5 post-generation verification."""
        # TODO(G1): Query current PostgreSQL Passage + DocumentVersion rows for passage_ids
        # and enforce audience filtering before Layer 5 verify_final_delivery (Worked Case 9).
        _ = user, passage_ids
        return {}
