# CDSCO-Style Regulatory Workflow Automation

Working FastAPI backend for AI-assisted regulatory workflow automation and data anonymisation, designed for CDSCO-like review flows and SUGAM / MD Online style integration.

## What This Model Does

The system implements all requested core modules:

- Data anonymisation with a two-step flow:
  - de-identification / pseudonymisation with secure tokens
  - irreversible anonymisation with masking and generalisation
- Document summarisation for:
  - SAE case narratives
  - clinical application text
  - meeting summaries
  - inspection notes
- Completeness assessment and consistency checks
- Case severity classification
- Duplicate detection
- Document comparison
- Report generation for:
  - inspection reports
  - consolidated regulatory evaluation review reports

## Architecture

- `app/models`: request and response schemas
- `app/services`: business logic for each NLP module
- `app/api`: FastAPI routes
- `app/utils`: shared text utilities
- `data`: mock datasets
- `tests`: smoke tests and endpoint checks

## Key Compliance Intent

The anonymisation module is shaped for alignment with:

- DPDP Act 2023
- NDHM
- ICMR guidance
- CDSCO reviewer workflows

This implementation is a production-style starter model, not a legal compliance certification system. Legal review is still required before live deployment.

## API Endpoints

- `GET /`
- `GET /health`
- `POST /anonymize`
- `POST /summarize`
- `POST /validate`
- `POST /classify`
- `POST /deduplicate`
- `POST /compare`
- `POST /generate-report`
- `POST /pipeline/run`

## Run

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

The root URL now opens a guided frontend where you can:

- paste narrative text
- enter structured form JSON
- add a previous version for comparison
- add duplicate candidate documents
- run the full pipeline
- download the generated report as a styled PDF

## Example: Two-Step Anonymisation

Request:

```json
{
  "text": "Patient Mr. Rajesh Kumar, 58 years old, called from 9876543210 and was admitted to Sunrise Hospital. DOB: 12/08/1966.",
  "pseudonymize": false,
  "structured_data": {
    "case_id": "SAE-001",
    "reporter_name": "Dr. Meena Shah"
  }
}
```

Response shape:

```json
{
  "deidentified_text": "Patient NAME_TOKEN_xxxxxxxx, AGE_TOKEN_xxxxxxxx, called from PHONE_TOKEN_xxxxxxxx and was admitted to HOSPITAL_TOKEN_xxxxxxxx. DOB_TOKEN_xxxxxxxx.",
  "anonymized_text": "Patient [NAME], [AGE_50s], called from [PHONE] and was admitted to [HOSPITAL]. [DOB_REDACTED]."
}
```

## Example: Summarisation

```json
{
  "text": "The SAE narrative reported a fatal adverse reaction after ICU admission. Follow-up causality assessment is pending.",
  "document_type": "sae_case"
}
```

## Example: Completeness Validation

```json
{
  "form_data": {
    "case_id": "SAE-001",
    "patient_age": "58",
    "gender": "male"
  },
  "extracted_text": "Reporter: Dr. Meena Shah. suspect product: DrugX. male patient. adverse event: severe rash.",
  "checklist_type": "sae_report"
}
```

## Example: Regulatory Review Report

`POST /pipeline/run`

```json
{
  "text": "Patient Mr. Rajesh Kumar, male, was admitted to ICU after a fatal reaction. Case ID: SAE-001. Follow-up causality assessment is pending.",
  "form_data": {
    "case_id": "SAE-001",
    "patient_age": "58",
    "gender": "male"
  },
  "documents": [
    {"document_id": "1", "text": "Patient admitted to ICU after a fatal reaction."},
    {"document_id": "2", "text": "Patient admitted to ICU after a fatal reaction."}
  ],
  "comparison_text": "Patient was admitted after reaction.",
  "document_type": "sae_case",
  "checklist_type": "sae_report",
  "metadata": {
    "portal": "SUGAM",
    "submission_id": "SUGAM-SAE-001"
  }
}
```

This returns:

- anonymized text
- structured summary
- completeness score and field gaps
- severity classification
- duplicate matches
- version comparison
- a final `Regulatory Evaluation Review Report`

## Example cURL Commands

Anonymize:

```bash
curl -X POST "http://127.0.0.1:8000/anonymize" \
  -H "Content-Type: application/json" \
  -d '{"text":"Patient Mr. Rajesh Kumar, 58 years old, called from 9876543210 and visited Sunrise Hospital.","pseudonymize":false}'
```

Pipeline:

```bash
curl -X POST "http://127.0.0.1:8000/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{"text":"Patient Mr. Rajesh Kumar, male, was admitted to ICU after a fatal reaction. Case ID: SAE-001.","form_data":{"case_id":"SAE-001","patient_age":"58","gender":"male"},"documents":[{"document_id":"1","text":"Patient admitted to ICU after a fatal reaction."},{"document_id":"2","text":"Patient admitted to ICU after a fatal reaction."}],"comparison_text":"Patient was admitted after reaction.","document_type":"sae_case","checklist_type":"sae_report"}'
```

## Current Model Strategy

The code is modular so you can upgrade each baseline independently:

- anonymisation:
  - current: hybrid regex/rule-based
  - next: spaCy + transformer NER
- summarisation:
  - current: structured extractive map-reduce
  - next: BART / T5 / LLM summarisation
- classification:
  - current: severity heuristic baseline
  - next: fine-tuned BERT
- deduplication:
  - current: fuzzy text similarity
  - next: SBERT + cosine similarity
- inspection report generation:
  - current: template-guided generator
  - next: LLM template filling + OCR handwriting pipeline

## Tests

```bash
python3 -m pytest
```

If `pytest` is not installed in your environment, install dependencies first inside the virtual environment.
