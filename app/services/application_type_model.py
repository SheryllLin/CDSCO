from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def build_record_text(row: dict[str, str]) -> str:
    return " | ".join(
        f"{key}: {value.strip()}"
        for key, value in row.items()
        if value and value.strip()
    )


class ApplicationTypeModelTrainer:
    MODEL_USED = "TF-IDF + Logistic Regression"

    def load_training_rows(self, dataset_map: dict[str, str]) -> tuple[list[str], list[str]]:
        texts: list[str] = []
        labels: list[str] = []

        for label, file_path in dataset_map.items():
            with open(file_path, newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    texts.append(build_record_text(row))
                    labels.append(label)

        if not texts:
            raise ValueError("No training rows were loaded from the provided datasets.")

        return texts, labels

    def train_and_save(
        self,
        dataset_map: dict[str, str],
        model_path: str | Path,
        metrics_path: str | Path,
    ) -> dict[str, object]:
        texts, labels = self.load_training_rows(dataset_map)
        x_train, x_test, y_train, y_test = train_test_split(
            texts,
            labels,
            test_size=0.2,
            random_state=42,
            stratify=labels,
        )

        pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
                ("classifier", LogisticRegression(max_iter=2000, random_state=42)),
            ]
        )
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        accuracy = accuracy_score(y_test, predictions)

        metrics = {
            "model_used": self.MODEL_USED,
            "accuracy": round(float(accuracy), 4),
            "train_size": len(x_train),
            "test_size": len(x_test),
            "labels": sorted(set(labels)),
            "class_distribution": dict(Counter(labels)),
            "classification_report": classification_report(y_test, predictions, output_dict=True),
            "dataset_files": dataset_map,
        }

        model_path = Path(model_path)
        metrics_path = Path(metrics_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(
            {
                "pipeline": pipeline,
                "model_used": self.MODEL_USED,
                "labels": sorted(set(labels)),
            },
            model_path,
        )
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        return metrics
