from app.models.schemas import (
    CompareResponse,
    DeduplicateDocument,
    DeduplicateResponse,
    PipelineRequest,
    PipelineResponse,
)
from app.services.anonymization import AnonymizationService
from app.services.classification import CaseClassificationService
from app.services.comparison import DocumentComparisonService
from app.services.completeness import CompletenessService
from app.services.deduplication import DuplicateDetectionService
from app.services.ocr import OCRService
from app.services.portal_integration import PortalIntegrationService
from app.services.report_generation import ReportGenerationService
from app.services.summarization import SummarizationService


class RegulatoryPipelineService:
    def __init__(self) -> None:
        self.ocr = OCRService()
        self.anonymizer = AnonymizationService()
        self.summarizer = SummarizationService()
        self.validator = CompletenessService()
        self.classifier = CaseClassificationService()
        self.deduplicator = DuplicateDetectionService()
        self.comparator = DocumentComparisonService()
        self.reporter = ReportGenerationService()
        self.portal_integration = PortalIntegrationService()

    def run(self, request: PipelineRequest) -> PipelineResponse:
        ocr_output = self.ocr.extract(request.text, source_type=request.source_type)
        anonymized = self.anonymizer.anonymize(
            ocr_output.extracted_text,
            pseudonymize=request.pseudonymize,
            structured_data=request.form_data,
        )
        summary = self.summarizer.summarize(
            anonymized.anonymized_text,
            document_type=request.document_type,
        )
        validation = self.validator.validate(
            request.form_data,
            anonymized.anonymized_text,
            checklist_type=request.checklist_type,
        )
        classification = self.classifier.classify(anonymized.anonymized_text)

        docs = request.documents or [
            DeduplicateDocument(document_id="primary", text=anonymized.anonymized_text)
        ]
        deduplication = self.deduplicator.deduplicate(docs)

        comparison: CompareResponse | None = None
        if request.comparison_text:
            comparison = self.comparator.compare(request.comparison_text, anonymized.anonymized_text)

        report = self.reporter.generate(
            anonymized.anonymized_text,
            report_type="regulatory_review",
            context={
                "summary": summary.model_dump(),
                "validation": validation.model_dump(),
                "classification": classification.model_dump(),
                "deduplication": deduplication.model_dump(),
                "comparison": comparison.model_dump() if comparison else None,
                "metadata": request.metadata.model_dump() if request.metadata else {},
                "document_type": request.document_type,
                "checklist_type": request.checklist_type,
                },
        )
        portal_payloads = self.portal_integration.prepare(
            form_data=request.form_data,
            document_type=request.document_type,
            checklist_type=request.checklist_type,
            metadata=request.metadata,
        )
        return PipelineResponse(
            ocr=ocr_output,
            anonymization=anonymized,
            summary=summary,
            validation=validation,
            classification=classification,
            deduplication=deduplication,
            comparison=comparison,
            report=report,
            portal_integration=portal_payloads,
        )
