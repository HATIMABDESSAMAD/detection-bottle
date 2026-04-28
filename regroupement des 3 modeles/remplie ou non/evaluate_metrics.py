from pathlib import Path
import json

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedShuffleSplit

SEED = 42
IMG_SIZE = (224, 224)
BATCH_SIZE = 8
DATASET_DIR = Path("dataset")
MODEL_PATH = Path("artifacts/models/best_resnet50v2.keras")
OUT_JSON = Path("artifacts/metrics_report.json")

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images_and_labels(root: Path):
    class_dirs = [d for d in sorted(root.iterdir()) if d.is_dir()]
    if not class_dirs:
        raise ValueError(f"No class folders found in: {root}")

    class_names = [d.name for d in class_dirs]
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}

    paths = []
    labels = []

    for class_dir in class_dirs:
        for p in sorted(class_dir.rglob("*")):
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
                paths.append(str(p))
                labels.append(class_to_idx[class_dir.name])

    if not paths:
        raise ValueError("No image files found in dataset folders.")

    return np.array(paths), np.array(labels), class_names


def stratified_split(paths, labels, seed=42):
    splitter_1 = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=seed)
    _, temp_idx = next(splitter_1.split(paths, labels))

    temp_paths = paths[temp_idx]
    temp_labels = labels[temp_idx]

    splitter_2 = StratifiedShuffleSplit(n_splits=1, test_size=0.50, random_state=seed)
    val_rel_idx, test_rel_idx = next(splitter_2.split(temp_paths, temp_labels))

    val_idx = temp_idx[val_rel_idx]
    test_idx = temp_idx[test_rel_idx]

    return val_idx, test_idx


def decode_and_resize(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.cast(img, tf.float32)
    return img, tf.cast(label, tf.int32)


def make_dataset(paths, labels):
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(decode_and_resize, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds


def specificity_from_cm(cm):
    if cm.shape != (2, 2):
        return float("nan")
    tn, fp, fn, tp = cm.ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0


def compute_split_metrics(model, x, y, class_names, split_name):
    ds = make_dataset(x, y)
    y_prob = model.predict(ds, verbose=0).ravel()
    y_pred = (y_prob >= 0.5).astype(int)

    cm = confusion_matrix(y, y_pred)

    metrics = {
        "split": split_name,
        "n_samples": int(len(y)),
        "accuracy": float(accuracy_score(y, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, y_pred)),
        "precision": float(precision_score(y, y_pred, zero_division=0)),
        "recall": float(recall_score(y, y_pred, zero_division=0)),
        "f1": float(f1_score(y, y_pred, zero_division=0)),
        "specificity": float(specificity_from_cm(cm)),
        "mcc": float(matthews_corrcoef(y, y_pred)) if len(np.unique(y_pred)) > 1 else 0.0,
        "log_loss": float(log_loss(y, y_prob, labels=[0, 1])),
        "auc": float(roc_auc_score(y, y_prob)),
        "confusion_matrix": cm.astype(int).tolist(),
        "classification_report": classification_report(
            y,
            y_pred,
            target_names=class_names,
            digits=4,
            output_dict=True,
            zero_division=0,
        ),
    }

    return metrics


def print_metrics(metrics):
    print("=" * 70)
    print(f"METRICS - {metrics['split'].upper()} (n={metrics['n_samples']})")
    print("=" * 70)
    print(f"Accuracy          : {metrics['accuracy']:.4f}")
    print(f"Balanced Accuracy : {metrics['balanced_accuracy']:.4f}")
    print(f"Precision         : {metrics['precision']:.4f}")
    print(f"Recall            : {metrics['recall']:.4f}")
    print(f"F1 Score          : {metrics['f1']:.4f}")
    print(f"Specificity       : {metrics['specificity']:.4f}")
    print(f"ROC AUC           : {metrics['auc']:.4f}")
    print(f"MCC               : {metrics['mcc']:.4f}")
    print(f"Log Loss          : {metrics['log_loss']:.4f}")
    print("Confusion Matrix  :")
    print(np.array(metrics["confusion_matrix"]))


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    paths, labels, class_names = list_images_and_labels(DATASET_DIR)
    val_idx, test_idx = stratified_split(paths, labels, seed=SEED)

    x_val, y_val = paths[val_idx], labels[val_idx]
    x_test, y_test = paths[test_idx], labels[test_idx]

    model = tf.keras.models.load_model(MODEL_PATH)

    val_metrics = compute_split_metrics(model, x_val, y_val, class_names, "validation")
    test_metrics = compute_split_metrics(model, x_test, y_test, class_names, "test")

    print_metrics(val_metrics)
    print_metrics(test_metrics)

    report = {
        "model_path": str(MODEL_PATH),
        "class_names": class_names,
        "validation": val_metrics,
        "test": test_metrics,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Saved metrics report: {OUT_JSON}")


if __name__ == "__main__":
    main()
