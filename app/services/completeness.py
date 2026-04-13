import re
from typing import Dict, List

from app.models.schemas import ValidateResponse


class CompletenessService:
    REQUIRED_FIELDS = {
        "sae_report": {
            "case_id": r"[A-Z0-9-]{4,}",
            "patient_age": r"\d{1,3}",
            "gender": r"(?i)(male|female|other)",
            "event_description": r".{10,}",
            "reporter_name": r".{3,}",
            "suspect_product": r".{2,}",
        },
        "clinical_application": {
            "application_id": r"[A-Z0-9-]{4,}",
            "applicant_name": r".{3,}",
            "study_title": r".{10,}",
            "indication": r".{3,}",
            "site_count": r"\d+",
            "ethics_committee_status": r".{2,}",
        },
    }

    def validate(
        self,
        form_data: Dict[str, str],
        extracted_text: str,
        checklist_type: str = "sae_report",
    ) -> ValidateResponse:
        required_fields = self.REQUIRED_FIELDS.get(checklist_type, self.REQUIRED_FIELDS["sae_report"])
        missing: List[str] = []
        invalid: Dict[str, str] = {}
        inferred: Dict[str, str] = {}
        consistency_flags: List[str] = []

        for field, pattern in required_fields.items():
            value = (form_data.get(field) or "").strip()
            if not value:
                inferred_value = self._infer_field(field, extracted_text)
                if inferred_value:
                    inferred[field] = inferred_value
                else:
                    missing.append(field)
                continue
            if not re.fullmatch(pattern, value):
                invalid[field] = f"Value '{value}' does not match expected format"

        consistency_flags.extend(self._consistency_checks(form_data, extracted_text, checklist_type))
        satisfied = len(required_fields) - len(missing) - len(invalid)
        score = int((satisfied / len(required_fields)) * 100)
        return ValidateResponse(
            completeness_score=score,
            missing_fields=missing,
            invalid_fields=invalid,
            inferred_fields=inferred,
            checklist_type=checklist_type,
            consistency_flags=consistency_flags,
        )

    def _infer_field(self, field: str, text: str) -> str | None:
        lookups = {
            "case_id": r"(?:Case ID|Subject ID|Reference No)\s*[:#-]\s*([A-Z0-9-]+)",
            "patient_age": r"(\d{1,3})\s*(?:years|yrs)\s*old",
            "gender": r"\b(male|female|other)\b",
            "reporter_name": r"(?:Reporter|Reported by)\s*[:#-]\s*([A-Za-z.\s]+)",
            "suspect_product": r"(?:suspect product|drug|device)\s*[:#-]\s*([A-Za-z0-9\s-]+)",
            "event_description": r"(?:event|reaction|adverse event)\s*[:#-]\s*(.+?)(?:\.|$)",
            "application_id": r"(?:Application ID|Submission ID|File No)\s*[:#-]\s*([A-Z0-9-]+)",
            "applicant_name": r"(?:Applicant|Sponsor)\s*[:#-]\s*([A-Za-z0-9.,\s]+)",
            "study_title": r"(?:Study Title|Protocol Title)\s*[:#-]\s*(.+?)(?:\.|$)",
            "indication": r"(?:Indication|Therapeutic Area)\s*[:#-]\s*(.+?)(?:\.|$)",
            "site_count": r"(?:Sites|Site Count)\s*[:#-]\s*(\d+)",
            "ethics_committee_status": r"(?:Ethics Committee|IEC)\s*[:#-]\s*([A-Za-z\s]+)",
        }
        pattern = lookups.get(field)
        if not pattern:
            return None
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return None
        return match.group(1).strip()

    def _consistency_checks(
        self,
        form_data: Dict[str, str],
        text: str,
        checklist_type: str,
    ) -> List[str]:
        flags: List[str] = []
        if checklist_type == "sae_report":
            gender = (form_data.get("gender") or "").lower()
            if gender and gender not in text.lower():
                flags.append("Gender provided in form does not appear in extracted narrative.")
            case_id = form_data.get("case_id")
            if case_id and case_id not in text:
                flags.append("Case ID present in form but not found in extracted text.")
        if checklist_type == "clinical_application":
            if form_data.get("site_count") and not re.search(r"\bsite", text, re.IGNORECASE):
                flags.append("Site count submitted in form is not substantiated in the narrative.")
            if form_data.get("ethics_committee_status") and "ethics" not in text.lower():
                flags.append("Ethics committee status not traceable in supporting text.")
        return flags
