from typing import Any, Dict, List

from app.models.schemas import GenerateReportResponse, GeneratedReport
from app.utils.text import keyword_sentences, sentence_split


class ReportGenerationService:
    def generate(
        self,
        notes: str,
        report_type: str = "inspection",
        context: Dict[str, Any] | None = None,
    ) -> GenerateReportResponse:
        context = context or {}
        if report_type == "regulatory_review":
            return self._generate_regulatory_review(notes, context)
        return self._generate_inspection_report(notes, context)

    def _generate_inspection_report(
        self,
        notes: str,
        context: Dict[str, Any],
    ) -> GenerateReportResponse:
        summary = sentence_split(notes)[:3]
        observations = keyword_sentences(notes, ["observed", "inspection", "found", "noticed", "verified"])[:5]
        violations = keyword_sentences(notes, ["violation", "non-compliance", "breach", "missing", "deviation"])[:5]
        recommendations = keyword_sentences(notes, ["recommend", "should", "must", "corrective", "action"])[:5]

        if not observations:
            observations = sentence_split(notes)[:3]
        if not violations:
            violations = ["No explicit violation sentence detected; manual regulatory review recommended."]
        if not recommendations:
            recommendations = ["Initiate CAPA workflow and request supporting evidence from the applicant."]

        next_actions = [
            "Validate factual observations against inspection evidence pack.",
            "Issue deficiency or observation memo to the applicant if required.",
            "Track CAPA submission and closure timeline.",
        ]
        risk_level = self._risk_level(violations, notes)
        return GenerateReportResponse(
            report=GeneratedReport(
                title="CDSCO Inspection Report Draft",
                summary=summary,
                observations=observations,
                violations=violations,
                recommendations=recommendations,
                next_actions=next_actions,
                risk_level=risk_level,
            ),
            generation_mode="template-guided-regulatory-reporting",
        )

    def _generate_regulatory_review(
        self,
        notes: str,
        context: Dict[str, Any],
    ) -> GenerateReportResponse:
        document_type = context.get("document_type", "submission")
        metadata = context.get("metadata", {})
        summary_points: List[str] = []
        observations: List[str] = []
        violations: List[str] = []
        recommendations: List[str] = []
        next_actions: List[str] = []

        digest = context.get("summary", {}).get("reviewer_digest", [])
        if digest:
            summary_points.extend(digest[:3])

        validation = context.get("validation", {})
        if validation:
            score = validation.get("completeness_score")
            checklist = validation.get("checklist_type", "submission")
            summary_points.append(f"{checklist} completeness score: {score}/100.")
            for field in validation.get("missing_fields", []):
                violations.append(f"Missing mandatory field: {field}.")
            for field, issue in validation.get("invalid_fields", {}).items():
                violations.append(f"Invalid field {field}: {issue}")
            for flag in validation.get("consistency_flags", []):
                observations.append(flag)

        classification = context.get("classification", {})
        if classification:
            summary_points.append(
                f"Suggested severity signal for reviewer attention: {classification.get('predicted_label', 'Other')}."
            )

        deduplication = context.get("deduplication", {})
        duplicate_pairs = deduplication.get("duplicates", [])
        if duplicate_pairs:
            observations.append(
                f"{len(duplicate_pairs)} potential duplicate submission pair(s) detected for reviewer verification."
            )

        comparison = context.get("comparison")
        if comparison:
            change_summary = comparison.get("change_summary", {})
            observations.append(
                "Version comparison detected "
                f"{change_summary.get('modified_count', 0)} modified, "
                f"{change_summary.get('added_count', 0)} added, and "
                f"{change_summary.get('removed_count', 0)} removed segment(s)."
            )

        if not summary_points:
            summary_points = sentence_split(notes)[:3]
        if not observations:
            observations = sentence_split(notes)[:3]
        if not violations:
            violations = ["No blocking compliance violation auto-detected; continue officer review."]

        observations.extend(self._document_specific_observations(document_type, notes))
        recommendations.extend(self._document_specific_recommendations(document_type, notes, validation))

        if "Death" in " ".join(summary_points):
            recommendations.append("Prioritize the case for immediate medical and regulatory review.")
        if duplicate_pairs:
            recommendations.append("Merge or cross-link suspected duplicate records before final assessment.")
        if validation.get("missing_fields"):
            recommendations.append("Raise a deficiency query for missing mandatory fields.")
        if comparison:
            recommendations.append("Review substantive changes before carrying forward prior conclusions.")
        if not recommendations:
            recommendations.append("Proceed with standard reviewer workflow and document final disposition.")

        portal = metadata.get("portal")
        title_prefix = f"{portal} " if portal else ""
        next_actions = [
            "Route report to the assigned CDSCO reviewer queue.",
            "Attach supporting anonymized narrative and checklist validation output.",
            "Record officer decision, follow-up queries, and closure timeline in SUGAM or MD Online.",
        ]
        risk_level = self._risk_level(violations, " ".join(summary_points + observations + sentence_split(notes)[:3]))

        return GenerateReportResponse(
            report=GeneratedReport(
                title=f"{title_prefix}Regulatory Evaluation Review Report",
                summary=self._compress_items(summary_points, 4),
                observations=self._compress_items(self._dedupe(observations), 4),
                violations=self._compress_items(violations, 4),
                recommendations=self._compress_items(self._dedupe(recommendations), 4),
                next_actions=next_actions,
                risk_level=risk_level,
            ),
            generation_mode="pipeline-synthesized-regulatory-review",
        )

    def _risk_level(self, violations: List[str], text: str) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ["death", "fatal", "critical", "major violation"]):
            return "high"
        if violations and len(violations) >= 2:
            return "medium"
        return "low"

    def _document_specific_observations(self, document_type: str, notes: str) -> List[str]:
        lowered = notes.lower()
        if document_type == "application":
            observations = ["Application narrative reviewed for administrative completeness and filing consistency."]
            if "pending" in lowered or "annexure" in lowered:
                observations.append("Submission text references pending supporting annexures or attachments.")
            if "ethics" in lowered:
                observations.append("Ethics or committee approval status is mentioned in the submission narrative.")
            return observations
        if document_type == "meeting":
            observations = ["Meeting narrative reviewed to surface decisions, follow-up owners, and unresolved items."]
            if "agreed" in lowered or "decision" in lowered:
                observations.append("The text contains decision-oriented language suitable for action tracking.")
            return observations
        if document_type == "inspection":
            observations = ["Inspection narrative reviewed to surface observations, deviations, and CAPA follow-up items."]
            if "missing" in lowered or "deviation" in lowered:
                observations.append("Operational gaps are explicitly described in the inspection note.")
            return observations
        observations = ["Case narrative reviewed to surface safety signals, outcome information, and follow-up needs."]
        if "hospital" in lowered or "icu" in lowered:
            observations.append("Narrative includes escalation or care-setting information relevant for reviewer prioritisation.")
        return observations

    def _document_specific_recommendations(
        self,
        document_type: str,
        notes: str,
        validation: Dict[str, Any],
    ) -> List[str]:
        lowered = notes.lower()
        recommendations: List[str] = []
        if document_type == "application":
            recommendations.append("Use this output as a filing support note and retain reviewer discretion for final acceptability.")
            if validation.get("missing_fields"):
                recommendations.append("Request missing administrative or checklist elements before advancing the application stage.")
            return recommendations
        if document_type == "meeting":
            recommendations.append("Convert extracted action items into a tracked follow-up list for the review team.")
            if "7 days" in lowered or "deadline" in lowered:
                recommendations.append("Monitor timeline-sensitive commitments referenced in the meeting narrative.")
            return recommendations
        if document_type == "inspection":
            recommendations.append("Use the draft as inspection support output and confirm all observations against source evidence.")
            if "corrective" in lowered or "capa" in lowered:
                recommendations.append("Track CAPA commitments and supporting evidence before closure.")
            return recommendations
        recommendations.append("Use the severity signal as review support only; it is not a final medical or regulatory conclusion.")
        if "pending" in lowered:
            recommendations.append("Request pending follow-up information before completing the review note.")
        return recommendations

    def _dedupe(self, items: List[str]) -> List[str]:
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    def _compress_items(self, items: List[str], limit: int) -> List[str]:
        compressed: List[str] = []
        for item in items:
            text = " ".join(str(item).split())
            if len(text) > 160:
                text = text[:157].rsplit(" ", 1)[0].rstrip(" ,;:") + "..."
            if text and text not in compressed:
                compressed.append(text)
            if len(compressed) >= limit:
                break
        return compressed
