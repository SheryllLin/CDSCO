from collections import OrderedDict

from app.models.schemas import ClassificationScore, ClassifyResponse


class CaseClassificationService:
    LABEL_KEYWORDS = OrderedDict(
        {
            "Death": ["death", "fatal", "expired", "deceased"],
            "Disability": ["disability", "disabled", "impairment", "paralysis"],
            "Hospitalization": ["hospitalized", "admitted", "icu", "hospitalisation", "hospitalization"],
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
            score = sum(1 for keyword in keywords if keyword in lowered) * self.LABEL_WEIGHTS[label]
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
            model_used="keyword-bert-ready-baseline",
        )
