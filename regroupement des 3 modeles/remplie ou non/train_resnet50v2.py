import os
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras import layers
from tensorflow.keras.applications.resnet_v2 import ResNet50V2, preprocess_input


SEED = 42
IMG_SIZE = (224, 224)
BATCH_SIZE = 8
EPOCHS_STAGE_1 = 40
EPOCHS_STAGE_2 = 40
FINE_TUNE_LAST_N = 40
DATASET_DIR = Path("dataset")
OUTPUT_DIR = Path("artifacts")


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"
tf.random.set_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)


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
        class_name = class_dir.name
        for p in sorted(class_dir.rglob("*")):
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
                paths.append(str(p))
                labels.append(class_to_idx[class_name])

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
    return img, tf.cast(label, tf.float32)


def make_dataset(paths, labels, training=False):
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if training:
        ds = ds.shuffle(buffer_size=len(paths), seed=SEED, reshuffle_each_iteration=True)
    ds = ds.map(decode_and_resize, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds


def build_model():
    data_augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.08),
            layers.RandomZoom(0.12),
            layers.RandomContrast(0.10),
        ],
        name="augmentation",
    )

    base_model = ResNet50V2(include_top=False, weights="imagenet", input_shape=IMG_SIZE + (3,))
    base_model.trainable = False

    inputs = layers.Input(shape=IMG_SIZE + (3,))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.35)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)

    model = tf.keras.Model(inputs, outputs, name="resnet50v2_binary")
    return model, base_model


def merge_histories(h1, h2):
    out = {}
    for key in set(list(h1.history.keys()) + list(h2.history.keys())):
        out[key] = h1.history.get(key, []) + h2.history.get(key, [])
    return out


def plot_history(history_dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    epochs = range(1, len(history_dict["loss"]) + 1)

    plt.figure(figsize=(13, 5))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, history_dict["loss"], label="train_loss")
    plt.plot(epochs, history_dict["val_loss"], label="val_loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Loss")
    plt.legend()

    plt.subplot(1, 2, 2)
    if "accuracy" in history_dict and "val_accuracy" in history_dict:
        plt.plot(epochs, history_dict["accuracy"], label="train_acc")
        plt.plot(epochs, history_dict["val_accuracy"], label="val_acc")
        plt.xlabel("Epoch")
        plt.ylabel("Accuracy")
        plt.title("Accuracy")
        plt.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    models_dir = OUTPUT_DIR / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    paths, labels, class_names = list_images_and_labels(DATASET_DIR)

    print("=" * 70)
    print("DATASET SUMMARY")
    print(f"Total images: {len(paths)}")
    for i, name in enumerate(class_names):
        print(f"  - {name}: {(labels == i).sum()}")
    print(f"Class index mapping: {dict(enumerate(class_names))}")
    print("=" * 70)

    train_idx, val_idx, test_idx = stratified_split(paths, labels, seed=SEED)

    x_train, y_train = paths[train_idx], labels[train_idx]
    x_val, y_val = paths[val_idx], labels[val_idx]
    x_test, y_test = paths[test_idx], labels[test_idx]

    print("SPLITS")
    print(f"Train: {len(x_train)} | Val: {len(x_val)} | Test: {len(x_test)}")

    train_ds = make_dataset(x_train, y_train, training=True)
    val_ds = make_dataset(x_val, y_val, training=False)
    test_ds = make_dataset(x_test, y_test, training=False)

    classes = np.unique(y_train)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    class_weight = {int(c): float(w) for c, w in zip(classes, weights)}
    print(f"Class weights: {class_weight}")

    model, base_model = build_model()

    checkpoint_best = models_dir / "best_resnet50v2.keras"
    callbacks_stage_1 = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(checkpoint_best),
            monitor="val_auc",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_auc",
            patience=10,
            mode="max",
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=4,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    print("\n" + "=" * 70)
    print("STAGE 1: Train classifier head (base frozen)")
    print("=" * 70)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )

    history_1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_STAGE_1,
        class_weight=class_weight,
        callbacks=callbacks_stage_1,
        verbose=1,
    )

    print("\n" + "=" * 70)
    print("STAGE 2: Fine-tuning upper ResNet blocks")
    print("=" * 70)

    base_model.trainable = True

    if FINE_TUNE_LAST_N > 0:
        for layer in base_model.layers[:-FINE_TUNE_LAST_N]:
            layer.trainable = False

    for layer in base_model.layers:
        if isinstance(layer, layers.BatchNormalization):
            layer.trainable = False

    callbacks_stage_2 = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(checkpoint_best),
            monitor="val_auc",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_auc",
            patience=10,
            mode="max",
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=4,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )

    history_2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_STAGE_1 + EPOCHS_STAGE_2,
        initial_epoch=len(history_1.history["loss"]),
        class_weight=class_weight,
        callbacks=callbacks_stage_2,
        verbose=1,
    )

    print("\n" + "=" * 70)
    print("EVALUATION")
    print("=" * 70)

    val_metrics = model.evaluate(val_ds, verbose=1)
    test_metrics = model.evaluate(test_ds, verbose=1)

    metric_names = model.metrics_names
    print("Validation metrics:")
    for name, value in zip(metric_names, val_metrics):
        print(f"  {name}: {value:.6f}")

    print("Test metrics:")
    for name, value in zip(metric_names, test_metrics):
        print(f"  {name}: {value:.6f}")

    final_model_path = models_dir / "final_resnet50v2.keras"
    model.save(final_model_path)
    print(f"Saved final model: {final_model_path}")
    print(f"Saved best checkpoint: {checkpoint_best}")

    merged_history = merge_histories(history_1, history_2)
    history_plot_path = OUTPUT_DIR / "training_curves.png"
    plot_history(merged_history, history_plot_path)
    print(f"Saved training curves: {history_plot_path}")


if __name__ == "__main__":
    main()
