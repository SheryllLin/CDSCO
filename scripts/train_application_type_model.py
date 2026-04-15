from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.application_type_model import ApplicationTypeModelTrainer


def main() -> None:
    dataset_map = {
        "Formulation and R&D": "/Users/sheryllmascarenhas/Downloads/formulation_rd_dataset.csv",
        "Dual Use NOC": "/Users/sheryllmascarenhas/Downloads/dual_use_noc_dataset.csv",
        "BA/BE Clinical Trials": "/Users/sheryllmascarenhas/Desktop/BA:BE_clinical_trials_dataset.csv",
        "Test License": "/Users/sheryllmascarenhas/Desktop/stage2_test_license.csv",
        "Registration of CDTL": "/Users/sheryllmascarenhas/Desktop/cdtl_registration_dataset.csv",
    }
    model_path = Path("data/models/application_type_classifier.joblib")
    metrics_path = Path("data/models/application_type_metrics.json")

    trainer = ApplicationTypeModelTrainer()
    metrics = trainer.train_and_save(dataset_map, model_path, metrics_path)

    print("Application type model training completed.")
    print(f"Model used: {metrics['model_used']}")
    print(f"Accuracy: {metrics['accuracy']}")
    print(f"Train size: {metrics['train_size']}")
    print(f"Test size: {metrics['test_size']}")
    print(f"Saved model: {model_path}")
    print(f"Saved metrics: {metrics_path}")


if __name__ == "__main__":
    main()
