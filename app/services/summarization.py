from typing import List

from app.core.config import get_settings
from app.models.schemas import StructuredSummary, SummarizeResponse
from app.services.base import OptionalDependencyMixin
from app.utils.text import chunk_text, keyword_sentences, sentence_split


class SummarizationService(OptionalDependencyMixin):
    KEYWORD_PROFILES = {
        "sae_case": {
            "findings": ["adverse", "reaction", "serious", "reported", "event"],
            "risks": ["risk", "history", "allergy", "comorbidity", "contraindication"],
            "outcomes": ["outcome", "recovered", "fatal", "death", "stabilized", "discharged"],
            "notes": ["follow-up", "pending", "causality", "narrative", "assessment"],
        },
        "application": {
            "findings": ["application", "submission", "study", "manufacturing", "module"],
            "risks": ["deficiency", "missing", "incomplete", "clarification", "deviation"],
            "outcomes": ["approved", "rejected", "pending", "query", "deferred"],
            "notes": ["undertaking", "annexure", "checklist", "compliance", "timeline"],
        },
        "meeting": {
            "findings": ["decision", "discussion", "agreed", "committee", "resolved"],
            "risks": ["concern", "risk", "issue", "escalation", "dependency"],
            "outcomes": ["approved", "deferred", "closed", "assigned", "accepted"],
            "notes": ["action item", "next step", "owner", "deadline", "follow-up"],
        },
        "inspection": {
            "findings": ["inspection", "observed", "found", "facility", "batch"],
            "risks": ["violation", "non-compliance", "deviation", "gap", "critical"],
            "outcomes": ["closed", "pending", "capa", "corrective", "resolved"],
            "notes": ["recommend", "timeline", "follow-up", "evidence", "submission"],
        },
    }

    def __init__(self) -> None:
        self.settings = get_settings()

    def summarize(
        self,
        text: str,
        max_chunk_chars: int | None = None,
        document_type: str = "sae_case",
    ) -> SummarizeResponse:
        limit = max_chunk_chars or self.settings.max_summary_chunk_chars
        chunks = chunk_text(text, limit) or [text]
        chunk_summaries = [self._summarize_chunk(chunk, document_type) for chunk in chunks]
        merged = self._merge(chunk_summaries)
        return SummarizeResponse(
            summary=merged,
            chunks_processed=len(chunks),
            model_used="hybrid-extractive-mapreduce",
            document_type=document_type,
            reviewer_digest=self._reviewer_digest(merged, document_type),
        )

    def _summarize_chunk(self, text: str, document_type: str) -> StructuredSummary:
        profile = self.KEYWORD_PROFILES.get(document_type, self.KEYWORD_PROFILES["sae_case"])
        findings = self._pick(text, profile["findings"])
        risks = self._pick(text, profile["risks"])
        outcomes = self._pick(text, profile["outcomes"])
        notes = self._pick(text, profile["notes"])
        return StructuredSummary(
            key_findings=findings,
            risk_factors=risks,
            patient_outcome=outcomes,
            important_notes=notes,
        )

    def _pick(self, text: str, keywords: List[str]) -> List[str]:
        hits = keyword_sentences(text, keywords)
        if hits:
            return hits[:3]
        return sentence_split(text)[:2]

    def _merge(self, summaries: List[StructuredSummary]) -> StructuredSummary:
        return StructuredSummary(
            key_findings=self._flatten([s.key_findings for s in summaries]),
            risk_factors=self._flatten([s.risk_factors for s in summaries]),
            patient_outcome=self._flatten([s.patient_outcome for s in summaries]),
            important_notes=self._flatten([s.important_notes for s in summaries]),
        )

    def _flatten(self, values: List[List[str]]) -> List[str]:
        flat: List[str] = []
        for items in values:
            for item in items:
                if item not in flat:
                    flat.append(item)
        return flat[:5]

    def _reviewer_digest(self, summary: StructuredSummary, document_type: str) -> List[str]:
        headings = {
            "sae_case": "SAE review",
            "application": "Application review",
            "meeting": "Meeting synthesis",
            "inspection": "Inspection digest",
        }
        prefix = headings.get(document_type, "Reviewer digest")
        digest: List[str] = []
        if summary.key_findings:
            digest.append(f"{prefix}: {summary.key_findings[0]}")
        if summary.risk_factors:
            digest.append(f"Primary risk signal: {summary.risk_factors[0]}")
        if summary.patient_outcome:
            digest.append(f"Current outcome: {summary.patient_outcome[0]}")
        if summary.important_notes:
            digest.append(f"Follow-up note: {summary.important_notes[0]}")
        return digest[:4]
