from __future__ import annotations

from app.models.schemas import PortalIntegrationResponse, PortalMetadata, PortalPayload


class PortalIntegrationService:
    def prepare(
        self,
        form_data: dict[str, str],
        document_type: str,
        checklist_type: str,
        metadata: PortalMetadata | None = None,
    ) -> PortalIntegrationResponse:
        metadata = metadata or PortalMetadata()
        submission_id = metadata.submission_id or form_data.get("application_id") or form_data.get("username") or "pending-submission"
        workflow_type = metadata.workflow_type or form_data.get("application_type") or form_data.get("trial_type") or document_type
        applicant_name = metadata.applicant_name or form_data.get("applicant_name") or form_data.get("organization_name") or "Unknown applicant"

        base_payload = {
            "submission_id": submission_id,
            "workflow_type": workflow_type,
            "document_type": document_type,
            "checklist_type": checklist_type,
            "applicant_name": applicant_name,
            "fields": {key: value for key, value in form_data.items() if value not in ("", None)},
        }
        payloads = [
            PortalPayload(
                portal="SUGAM",
                submission_id=submission_id,
                payload={**base_payload, "portal": "SUGAM", "routing": "clinical-review"},
                checklist_type=checklist_type,
                document_type=document_type,
            ),
            PortalPayload(
                portal="MD Online",
                submission_id=submission_id,
                payload={**base_payload, "portal": "MD Online", "routing": "medical-device-or-market-review"},
                checklist_type=checklist_type,
                document_type=document_type,
            ),
        ]
        return PortalIntegrationResponse(
            payloads=payloads,
            integration_mode="portal-ready-payload-preparation",
            recommendations=[
                "Map generated payload fields to authenticated SUGAM submission APIs when available.",
                "Reuse the same normalized payload for MD Online with portal-specific routing and validation adapters.",
                "Persist audit logs for reviewer actions, submission status, and follow-up deficiency queries.",
            ],
        )
