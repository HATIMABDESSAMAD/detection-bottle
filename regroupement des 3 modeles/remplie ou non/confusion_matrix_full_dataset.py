from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix

IMG_SIZE = (224, 224)
BATCH_SIZE = 8
DATASET_DIR = Path("dataset")
MODEL_PATH = Path("artifacts/models/best_resnet50v2.keras")
OUTPUT_PATH = Path("artifacts/confusion_matrix_full_dataset.png")

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


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    x_all, y_all, class_names = list_images_and_labels(DATASET_DIR)
    ds_all = make_dataset(x_all, y_all)

    model = tf.keras.models.load_model(MODEL_PATH)
    y_prob = model.predict(ds_all, verbose=1).ravel()
    y_pred = (y_prob >= 0.5).astype(int)

    cm = confusion_matrix(y_all, y_pred)
    print("Confusion matrix (full dataset):")
    print(cm)

    print("\nClassification report (full dataset):")
    print(classification_report(y_all, y_pred, target_names=class_names, digits=4))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(cmap="Blues", values_format="d", ax=ax, colorbar=False)
    plt.title("Confusion Matrix - Full Dataset")
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=160)
    plt.close(fig)

    print(f"Saved confusion matrix figure: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
