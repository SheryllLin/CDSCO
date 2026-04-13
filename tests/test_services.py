from fastapi.testclient import TestClient

from app.main import app
from app.services.anonymization import AnonymizationService
from app.services.comparison import DocumentComparisonService
from app.services.completeness import CompletenessService
from app.services.deduplication import DuplicateDetectionService


client = TestClient(app)


def test_anonymization_masks_entities() -> None:
    service = AnonymizationService()
    result = service.anonymize(
        "Patient Mr. Rajesh Kumar called from 9876543210 and was admitted to Sunrise Hospital."
    )
    assert "TOKEN" in result.deidentified_text
    assert "[NAME]" in result.anonymized_text
    assert "[PHONE]" in result.anonymized_text
    assert "[HOSPITAL]" in result.anonymized_text


def test_completeness_detects_missing_fields() -> None:
    service = CompletenessService()
    result = service.validate(
        {"case_id": "SAE-001", "patient_age": "58"},
        "Reporter: Dr. Meena Shah. suspect product: DrugX. male patient. adverse event: severe rash.",
    )
    assert result.completeness_score < 100
    assert "event_description" not in result.missing_fields
    assert result.checklist_type == "sae_report"


def test_duplicate_detection_finds_fuzzy_pair() -> None:
    response = client.post(
        "/deduplicate",
        json={
            "documents": [
                {"document_id": "1", "text": "Patient was hospitalized after adverse event."},
                {"document_id": "2", "text": "Patient was hospitalised after adverse event."},
            ],
            "similarity_threshold": 0.8,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["duplicates"]) == 1


def test_compare_endpoint_returns_modifications() -> None:
    service = DocumentComparisonService()
    result = service.compare(
        "The inspection found missing signatures. CAPA was pending.",
        "The inspection found missing signatures and incomplete labels. CAPA was submitted.",
    )
    assert result.modified
    assert result.change_summary["modified_count"] >= 1


def test_pipeline_endpoint() -> None:
    response = client.post(
        "/pipeline/run",
        json={
            "text": "Patient Mr. Rajesh Kumar, male, was admitted to ICU after a fatal reaction. Case ID: SAE-001.",
            "form_data": {"case_id": "SAE-001", "patient_age": "58", "gender": "male"},
            "documents": [
                {"document_id": "1", "text": "Patient admitted to ICU after a fatal reaction."},
                {"document_id": "2", "text": "Patient admitted to ICU after a fatal reaction."},
            ],
            "comparison_text": "Patient was admitted after reaction.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["classification"]["predicted_label"] == "Death"
    assert body["deduplication"]["duplicates"]
    assert body["report"]["report"]["title"] == "Regulatory Evaluation Review Report"
