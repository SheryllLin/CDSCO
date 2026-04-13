from difflib import SequenceMatcher
from typing import List

from app.core.config import get_settings
from app.models.schemas import DeduplicateDocument, DeduplicateResponse, DuplicatePair


class DuplicateDetectionService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def deduplicate(
        self,
        documents: List[DeduplicateDocument],
        similarity_threshold: float | None = None,
    ) -> DeduplicateResponse:
        threshold = similarity_threshold or self.settings.duplicate_similarity_threshold
        duplicates: List[DuplicatePair] = []

        for idx, left in enumerate(documents):
            for right in documents[idx + 1 :]:
                similarity = self._similarity(left.text, right.text)
                if similarity >= threshold:
                    duplicate_type = "exact" if similarity == 1.0 else "fuzzy"
                    duplicates.append(
                        DuplicatePair(
                            document_id_a=left.document_id,
                            document_id_b=right.document_id,
                            similarity=round(similarity, 4),
                            duplicate_type=duplicate_type,
                        )
                    )
        return DeduplicateResponse(duplicates=duplicates, total_documents=len(documents))

    def _similarity(self, left: str, right: str) -> float:
        return SequenceMatcher(None, left.lower().strip(), right.lower().strip()).ratio()
