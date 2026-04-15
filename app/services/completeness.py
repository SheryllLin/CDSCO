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
        "babe_clinical": {
            "application_id": r"[A-Z0-9-]{4,}",
            "study_title": r".{10,}",
            "sponsor_name": r".{2,}",
            "trial_site": r".{2,}",
            "drug_name": r".{2,}",
            "number_of_subjects": r"\d+",
        },
        "formulation_rd": {
            "rd_registration_number": r"[A-Z0-9-]{4,}",
            "product_category": r".{2,}",
            "dosage_form": r".{2,}",
            "research_area": r".{2,}",
            "number_of_scientists": r"\d+",
            "gmp_certified": r"(?i)(yes|no|true|false)",
        },
        "dual_use_noc": {
            "consignment_reference_number": r"[A-Z0-9-]{4,}",
            "item_category": r".{2,}",
            "item_description": r".{5,}",
            "quantity": r".{1,}",
            "end_use_purpose": r".{3,}",
            "iec_number": r".{3,}",
        },
        "cosmetics_registration": {
            "organization_name": r".{3,}",
            "brand_name": r".{2,}",
            "product_name": r".{2,}",
            "product_type": r".{2,}",
            "cosmetic_category": r".{2,}",
            "ingredient_summary": r".{3,}",
        },
        "test_license": {
            "application_id": r"[A-Z0-9-]{4,}",
            "license_type": r".{2,}",
            "drug_name": r".{2,}",
            "test_type": r".{2,}",
            "quantity_of_sample": r".{1,}",
            "testing_lab_name": r".{2,}",
        },
        "cdtl_registration": {
            "application_id": r"[A-Z0-9-]{4,}",
            "application_type": r".{2,}",
            "lab_name": r".{2,}",
            "lab_type": r".{2,}",
            "number_of_technical_staff": r"\d+",
            "test_capabilities": r".{2,}",
        },
    }
    FIELD_ALIASES = {
        "rd_registration_number": ["rd_registration_number", "r&d registration number"],
        "consignment_reference_number": ["consignment_reference_number", "consignment reference number"],
        "item_category": ["item_category", "item category"],
        "item_description": ["item_description", "item description"],
        "end_use_purpose": ["end_use_purpose", "end use purpose"],
        "iec_number": ["iec_number", "iec number"],
        "brand_name": ["brand_name", "brand name"],
        "product_name": ["product_name", "product name"],
        "cosmetic_category": ["cosmetic_category", "cosmetic category"],
        "ingredient_summary": ["ingredient_summary", "ingredients_list", "ingredient summary"],
        "number_of_subjects": ["number_of_subjects", "number of subjects"],
        "number_of_technical_staff": ["number_of_technical_staff", "number of technical staff"],
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
            value = self._get_value(form_data, field)
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
        # Inferred fields help the reviewer, but they should not score the same as
        # values supplied directly in the structured submission.
        satisfied = len(required_fields) - len(missing) - len(invalid) - len(inferred)
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
        if checklist_type == "formulation_rd":
            if self._get_value(form_data, "gmp_certified") and "gmp" not in text.lower():
                flags.append("GMP certification claim is not traceable in supporting text.")
        if checklist_type == "dual_use_noc":
            if self._get_value(form_data, "controlled_substance_flag") and "controlled" not in text.lower():
                flags.append("Controlled substance status is not explained in the supporting narrative.")
        if checklist_type == "cosmetics_registration":
            if self._get_value(form_data, "label_compliance") and "label" not in text.lower():
                flags.append("Label compliance declaration is not traceable in supporting text.")
        return flags

    def _get_value(self, form_data: Dict[str, str], field: str) -> str:
        aliases = self.FIELD_ALIASES.get(field, [field])
        for alias in aliases:
            value = str(form_data.get(alias) or "").strip()
            if value:
                return value
        return ""
