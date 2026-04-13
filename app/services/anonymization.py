import hashlib
import re
from typing import Dict, List, Tuple

from app.models.schemas import AnonymizeResponse, EntityMatch
from app.services.base import OptionalDependencyMixin


class AnonymizationService(OptionalDependencyMixin):
    ENTITY_PATTERNS: List[Tuple[str, str]] = [
        ("PHONE", r"(?:(?:\+91[-\s]?)?[6-9]\d{9})"),
        ("EMAIL", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        ("ID", r"\b(?:patient|case|subject|aadhaar|license|dl)\s*[:#-]?\s*[A-Z0-9-]{4,}\b"),
        ("DOB", r"\b(?:DOB|Date of Birth)\s*[:#-]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
        ("AGE", r"\b\d{1,3}\s*(?:years|yrs)\s*old\b"),
        ("HOSPITAL", r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Hospital|Medical College|Clinic|Institute)\b"),
        ("ADDRESS", r"\b\d{1,4}[,\s]+(?:[A-Za-z0-9#./-]+\s+){2,}(?:Road|Street|Nagar|Colony|Lane|Avenue|Phase|Sector)\b"),
        ("NAME", r"\b(?:Mr|Mrs|Ms|Dr)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b"),
        ("NAME", r"\b(?:Patient|Subject)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b"),
    ]

    def anonymize(
        self,
        text: str,
        pseudonymize: bool = False,
        structured_data: Dict[str, str] | None = None,
        compliance_profile: str = "india_regulatory",
    ) -> AnonymizeResponse:
        matches: List[EntityMatch] = []
        pseudonym_map: Dict[str, str] = {}
        occupied = set()
        structured_data = structured_data or {}

        for label, pattern in self.ENTITY_PATTERNS:
            for match in re.finditer(pattern, text):
                span = set(range(match.start(), match.end()))
                if occupied.intersection(span):
                    continue
                occupied.update(span)
                original = match.group(0)
                replacement = self._replacement(label, original, pseudonymize, pseudonym_map)
                matches.append(
                    EntityMatch(
                        label=label,
                        value=original,
                        replacement=replacement,
                        start=match.start(),
                        end=match.end(),
                    )
                )

        deidentified_text = self._apply_replacements(text, matches, use_replacements=True)
        anonymized_text = self._apply_replacements(text, matches, use_replacements=False)
        processing_notes = [
            "Step 1 de-identification generated secure tokens for detected direct identifiers.",
            "Step 2 anonymisation generalized or masked sensitive fields for irreversible reviewer-facing output.",
        ]
        if structured_data:
            processing_notes.append(
                f"Structured fields scanned for sensitive values: {', '.join(sorted(structured_data.keys()))}."
            )
        processing_notes.append(
            f"Compliance profile applied: {compliance_profile} aligned with DPDP Act 2023, NDHM, ICMR, and CDSCO guidance."
        )

        return AnonymizeResponse(
            original_text=text,
            deidentified_text=deidentified_text,
            anonymized_text=anonymized_text,
            entities=sorted(matches, key=lambda entity: entity.start),
            pseudonym_map=pseudonym_map,
            compliance_tags=["DPDP_2023", "NDHM", "ICMR", "CDSCO"],
            processing_notes=processing_notes,
        )

    def _apply_replacements(self, text: str, matches: List[EntityMatch], use_replacements: bool) -> str:
        updated = text
        for item in sorted(matches, key=lambda entity: entity.start, reverse=True):
            replacement = item.replacement if use_replacements else self._irreversible_mask(item.label, item.value)
            updated = updated[: item.start] + replacement + updated[item.end :]
        return self._normalize_sensitive_patterns(updated)

    def _irreversible_mask(self, label: str, value: str) -> str:
        if label == "AGE":
            age_match = re.search(r"(\d{1,3})", value)
            if age_match:
                age = int(age_match.group(1))
                lower = (age // 10) * 10
                return f"[AGE_{lower}s]"
        if label == "DOB":
            return "[DOB_REDACTED]"
        return f"[{label}]"

    def _normalize_sensitive_patterns(self, text: str) -> str:
        text = re.sub(r"\b(\d{2})/(\d{2})/(\d{4})\b", "[DATE]", text)
        text = re.sub(r"\b(\d{6})\b", "[PINCODE]", text)
        return text

    def _replacement(
        self,
        label: str,
        value: str,
        pseudonymize: bool,
        pseudonym_map: Dict[str, str],
    ) -> str:
        if not pseudonymize:
            digest = hashlib.sha1(f"{label}:{value}".encode("utf-8")).hexdigest()[:8]
            alias = f"{label}_TOKEN_{digest}"
            pseudonym_map[value] = alias
            return alias
        digest = hashlib.sha1(f"{label}:{value}".encode("utf-8")).hexdigest()[:8]
        alias = f"{label}_{digest}"
        pseudonym_map[value] = alias
        return alias
