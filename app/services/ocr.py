from __future__ import annotations

import re

from app.models.schemas import OCRResponse
from app.utils.text import normalize_whitespace


class OCRService:
    def extract(self, text: str, source_type: str = "typed") -> OCRResponse:
        cleaned = self._normalize(text)
        preprocessing_steps = [
            "Normalized whitespace and merged wrapped lines.",
            "Corrected common OCR ambiguities for identifiers and dates.",
            "Prepared reviewer-friendly extracted text for downstream NLP pipeline.",
        ]
        engine_used = "rule-based-text-normalizer"
        confidence_note = "Direct text input processed without image OCR." if source_type == "typed" else "OCR-style normalization applied to noisy inspection or scanned input."
        return OCRResponse(
            extracted_text=cleaned,
            source_type=source_type,
            engine_used=engine_used,
            confidence_note=confidence_note,
            preprocessing_steps=preprocessing_steps,
        )

    def _normalize(self, text: str) -> str:
        normalized = text.replace("\r", "\n")
        normalized = re.sub(r"(?<=\w)-\n(?=\w)", "", normalized)
        normalized = normalized.replace("\n", " ")
        normalized = re.sub(r"\b0(?=[A-Z])", "O", normalized)
        normalized = re.sub(r"(?<=[A-Z])1(?=[A-Z])", "I", normalized)
        normalized = re.sub(r"\s*[:;]\s*", ": ", normalized)
        return normalize_whitespace(normalized)
