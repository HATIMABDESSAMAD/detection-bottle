from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedShuffleSplit

SEED = 42
IMG_SIZE = (224, 224)
BATCH_SIZE = 8
DATASET_DIR = Path("dataset")
MODEL_PATH = Path("artifacts/models/best_resnet50v2.keras")
OUTPUT_PATH = Path("artifacts/confusion_matrix_test.png")

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
    train_idx, temp_idx = next(splitter_1.split(paths, labels))

    temp_paths = paths[temp_idx]
    temp_labels = labels[temp_idx]

    splitter_2 = StratifiedShuffleSplit(n_splits=1, test_size=0.50, random_state=seed)
    val_rel_idx, test_rel_idx = next(splitter_2.split(temp_paths, temp_labels))

    val_idx = temp_idx[val_rel_idx]
    test_idx = temp_idx[test_rel_idx]

    return train_idx, val_idx, test_idx


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

    paths, labels, class_names = list_images_and_labels(DATASET_DIR)
    _, _, test_idx = stratified_split(paths, labels, seed=SEED)

    x_test = paths[test_idx]
    y_test = labels[test_idx]

    model = tf.keras.models.load_model(MODEL_PATH)
    test_ds = make_dataset(x_test, y_test)

    y_prob = model.predict(test_ds, verbose=1).ravel()
    y_pred = (y_prob >= 0.5).astype(int)

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion matrix (test):")
    print(cm)

    print("\nClassification report (test):")
    print(classification_report(y_test, y_pred, target_names=class_names, digits=4))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(cmap="Blues", values_format="d", ax=ax, colorbar=False)
    plt.title("Confusion Matrix - Test Set")
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=160)
    plt.close(fig)

    print(f"Saved confusion matrix figure: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
