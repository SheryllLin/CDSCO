from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PortalMetadata(BaseModel):
    portal: Optional[str] = Field(default=None, description="SUGAM or MD Online")
    submission_id: Optional[str] = None
    applicant_name: Optional[str] = None


class AnonymizeRequest(BaseModel):
    text: str
    pseudonymize: bool = False
    source_type: str = "raw_text"
    compliance_profile: str = "india_regulatory"
    structured_data: Dict[str, str] = Field(default_factory=dict)
    metadata: Optional[PortalMetadata] = None


class EntityMatch(BaseModel):
    label: str
    value: str
    replacement: str
    start: int
    end: int


class AnonymizeResponse(BaseModel):
    original_text: str
    deidentified_text: str
    anonymized_text: str
    entities: List[EntityMatch]
    pseudonym_map: Dict[str, str]
    compliance_tags: List[str]
    processing_notes: List[str]


class SummarizeRequest(BaseModel):
    text: str
    max_chunk_chars: Optional[int] = None
    document_type: str = "sae_case"


class StructuredSummary(BaseModel):
    key_findings: List[str]
    risk_factors: List[str]
    patient_outcome: List[str]
    important_notes: List[str]


class SummarizeResponse(BaseModel):
    summary: StructuredSummary
    chunks_processed: int
    model_used: str
    document_type: str
    reviewer_digest: List[str]


class ValidateRequest(BaseModel):
    form_data: Dict[str, str]
    extracted_text: str
    checklist_type: str = "sae_report"


class ValidateResponse(BaseModel):
    completeness_score: int
    missing_fields: List[str]
    invalid_fields: Dict[str, str]
    inferred_fields: Dict[str, str]
    checklist_type: str
    consistency_flags: List[str]


class ClassifyRequest(BaseModel):
    text: str


class ClassificationScore(BaseModel):
    label: str
    score: float


class ClassifyResponse(BaseModel):
    predicted_label: str
    scores: List[ClassificationScore]
    model_used: str


class DeduplicateDocument(BaseModel):
    document_id: str
    text: str


class DeduplicateRequest(BaseModel):
    documents: List[DeduplicateDocument]
    similarity_threshold: Optional[float] = None


class DuplicatePair(BaseModel):
    document_id_a: str
    document_id_b: str
    similarity: float
    duplicate_type: str


class DeduplicateResponse(BaseModel):
    duplicates: List[DuplicatePair]
    total_documents: int


class CompareRequest(BaseModel):
    old_text: str
    new_text: str


class ModifiedSegment(BaseModel):
    before: str
    after: str


class CompareResponse(BaseModel):
    added: List[str]
    removed: List[str]
    modified: List[ModifiedSegment]
    unified_diff: str
    change_summary: Dict[str, int]


class GenerateReportRequest(BaseModel):
    notes: str
    report_type: str = "inspection"
    context: Dict[str, Any] = Field(default_factory=dict)


class GeneratedReport(BaseModel):
    title: str
    summary: List[str]
    observations: List[str]
    violations: List[str]
    recommendations: List[str]
    next_actions: List[str]
    risk_level: str


class GenerateReportResponse(BaseModel):
    report: GeneratedReport
    generation_mode: str


class PipelineRequest(BaseModel):
    text: str
    form_data: Dict[str, str] = Field(default_factory=dict)
    comparison_text: Optional[str] = None
    documents: List[DeduplicateDocument] = Field(default_factory=list)
    pseudonymize: bool = False
    document_type: str = "sae_case"
    checklist_type: str = "sae_report"
    metadata: Optional[PortalMetadata] = None


class PipelineResponse(BaseModel):
    anonymization: AnonymizeResponse
    summary: SummarizeResponse
    validation: ValidateResponse
    classification: ClassifyResponse
    deduplication: DeduplicateResponse
    comparison: Optional[CompareResponse]
    report: GenerateReportResponse


class ExportReportRequest(BaseModel):
    analysis: PipelineResponse
    portal: str = "SUGAM"
    document_type: str = "sae_case"
    generated_by: str = "Regulatory Workflow Automation API"
