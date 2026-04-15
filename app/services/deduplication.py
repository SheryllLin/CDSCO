from difflib import SequenceMatcher
from typing import List

from app.core.config import get_settings
from app.models.schemas import DeduplicateDocument, DeduplicateResponse, DuplicatePair
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
        tfidf_similarities = self._tfidf_similarity_map(documents)

        for idx, left in enumerate(documents):
            for right in documents[idx + 1 :]:
                sequence_similarity = self._similarity(left.text, right.text)
                semantic_similarity = tfidf_similarities.get((left.document_id, right.document_id), sequence_similarity)
                similarity = max(sequence_similarity, semantic_similarity)
                if similarity >= threshold:
                    if similarity == 1.0:
                        duplicate_type = "exact"
                    elif semantic_similarity >= threshold and semantic_similarity >= sequence_similarity:
                        duplicate_type = "semantic"
                    else:
                        duplicate_type = "fuzzy"
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

    def _tfidf_similarity_map(self, documents: List[DeduplicateDocument]) -> dict[tuple[str, str], float]:
        if len(documents) < 2:
            return {}
        texts = [doc.text for doc in documents]
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
        matrix = vectorizer.fit_transform(texts)
        scores = cosine_similarity(matrix)
        similarity_map: dict[tuple[str, str], float] = {}
        for idx, left in enumerate(documents):
            for jdx in range(idx + 1, len(documents)):
                similarity_map[(left.document_id, documents[jdx].document_id)] = float(scores[idx, jdx])
        return similarity_map
