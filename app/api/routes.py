from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.models.schemas import (
    AnonymizeRequest,
    AnonymizeResponse,
    ClassifyRequest,
    ClassifyResponse,
    CompareRequest,
    CompareResponse,
    DeduplicateRequest,
    DeduplicateResponse,
    ExportReportRequest,
    GenerateReportRequest,
    GenerateReportResponse,
    InspectionReportRequest,
    InspectionReportResponse,
    OCRRequest,
    OCRResponse,
    PipelineRequest,
    PipelineResponse,
    SummarizeRequest,
    SummarizeResponse,
    ValidateRequest,
    ValidateResponse,
)
from app.services.anonymization import AnonymizationService
from app.services.classification import CaseClassificationService
from app.services.comparison import DocumentComparisonService
from app.services.completeness import CompletenessService
from app.services.deduplication import DuplicateDetectionService
from app.services.pipeline import RegulatoryPipelineService
from app.services.pdf_report import PDFReportService
from app.services.ocr import OCRService
from app.services.report_generation import ReportGenerationService
from app.services.summarization import SummarizationService

router = APIRouter()

ocr_service = OCRService()
anonymizer = AnonymizationService()
summarizer = SummarizationService()
validator = CompletenessService()
classifier = CaseClassificationService()
deduplicator = DuplicateDetectionService()
comparator = DocumentComparisonService()
reporter = ReportGenerationService()
pipeline = RegulatoryPipelineService()
pdf_reporter = PDFReportService()


@router.post("/ocr", response_model=OCRResponse)
def extract_ocr(request: OCRRequest) -> OCRResponse:
    return ocr_service.extract(request.text, source_type=request.source_type)


@router.post("/anonymize", response_model=AnonymizeResponse)
def anonymize(request: AnonymizeRequest) -> AnonymizeResponse:
    return anonymizer.anonymize(
        request.text,
        pseudonymize=request.pseudonymize,
        structured_data=request.structured_data,
        compliance_profile=request.compliance_profile,
    )


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    return summarizer.summarize(
        request.text,
        max_chunk_chars=request.max_chunk_chars,
        document_type=request.document_type,
    )


@router.post("/validate", response_model=ValidateResponse)
def validate(request: ValidateRequest) -> ValidateResponse:
    return validator.validate(
        request.form_data,
        request.extracted_text,
        checklist_type=request.checklist_type,
    )


@router.post("/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest) -> ClassifyResponse:
    return classifier.classify(request.text)


@router.post("/deduplicate", response_model=DeduplicateResponse)
def deduplicate(request: DeduplicateRequest) -> DeduplicateResponse:
    return deduplicator.deduplicate(request.documents, similarity_threshold=request.similarity_threshold)


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    return comparator.compare(request.old_text, request.new_text)


@router.post("/generate-report", response_model=GenerateReportResponse)
def generate_report(request: GenerateReportRequest) -> GenerateReportResponse:
    return reporter.generate(
        request.notes,
        report_type=request.report_type,
        context=request.context,
    )


@router.post("/inspection-report", response_model=InspectionReportResponse)
def inspection_report(request: InspectionReportRequest) -> InspectionReportResponse:
    ocr_result = ocr_service.extract(request.text, source_type=request.source_type)
    report = reporter.generate(
        ocr_result.extracted_text,
        report_type="inspection",
        context=request.context,
    )
    return InspectionReportResponse(ocr=ocr_result, report=report)


@router.post("/pipeline/run", response_model=PipelineResponse)
def run_pipeline(request: PipelineRequest) -> PipelineResponse:
    return pipeline.run(request)


@router.post("/export-report")
def export_report(request: ExportReportRequest) -> StreamingResponse:
    pdf_bytes = pdf_reporter.build_pdf(
        analysis=request.analysis,
        portal=request.portal,
        document_type=request.document_type,
        generated_by=request.generated_by,
    )
    filename = f"regulatory_report_{request.document_type}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
