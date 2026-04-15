from collections import OrderedDict

from app.models.schemas import ClassificationScore, ClassifyResponse


class CaseClassificationService:
    LABEL_KEYWORDS = OrderedDict(
        {
            "Death": ["death", "fatal", "expired", "deceased", "mortality"],
            "Disability": ["disability", "disabled", "impairment", "paralysis", "permanent damage"],
            "Hospitalization": ["hospitalized", "admitted", "icu", "hospitalisation", "hospitalization", "inpatient"],
            "Other": [],
        }
    )
    LABEL_WEIGHTS = {
        "Death": 2.5,
        "Disability": 1.8,
        "Hospitalization": 1.3,
        "Other": 0.15,
    }

    def classify(self, text: str) -> ClassifyResponse:
        lowered = text.lower()
        raw_scores = []
        for label, keywords in self.LABEL_KEYWORDS.items():
            if not keywords:
                raw_scores.append((label, self.LABEL_WEIGHTS[label]))
                continue
            score = sum(lowered.count(keyword) for keyword in keywords) * self.LABEL_WEIGHTS[label]
            score += self._context_bonus(label, lowered)
            raw_scores.append((label, float(score)))

        total = sum(score for _, score in raw_scores) or 1.0
        normalized = [
            ClassificationScore(label=label, score=round(score / total, 4))
            for label, score in raw_scores
        ]
        predicted = max(normalized, key=lambda item: item.score).label
        if any(keyword in lowered for keyword in self.LABEL_KEYWORDS["Death"]):
            predicted = "Death"
        return ClassifyResponse(
            predicted_label=predicted,
            scores=normalized,
            model_used="hybrid-keyword-context-baseline",
        )

    def _context_bonus(self, label: str, lowered: str) -> float:
        if label == "Death" and any(term in lowered for term in ["post mortem", "cause of death", "died on"]):
            return 2.0
        if label == "Disability" and any(term in lowered for term in ["long-term impairment", "residual disability"]):
            return 1.2
        if label == "Hospitalization" and any(term in lowered for term in ["emergency room", "icu stay", "prolonged admission"]):
            return 1.0
        return 0.0
