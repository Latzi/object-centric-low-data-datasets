from __future__ import annotations

import json
import random
import shutil
from pathlib import Path


# ============================================================
# LOCAL INPUT / OUTPUT PATHS
# ============================================================

# Change this only if your local processed Cityscapes folder is elsewhere.
PROCESSED_DIR = Path(r"C:\Users\richm\Downloads\Cityscapes\processed")

# Output of script 03_create_yolo_annotations_from_filtered.py
SOURCE_YOLO_DIR = PROCESSED_DIR / "filtered_yolo"
SOURCE_IMAGES_DIR = SOURCE_YOLO_DIR / "images"
SOURCE_LABELS_DIR = SOURCE_YOLO_DIR / "labels"

# New local training-ready output
OUTPUT_DIR = PROCESSED_DIR / "Train_Data"
OUT_IMAGES_TRAIN = OUTPUT_DIR / "images" / "train"
OUT_IMAGES_VAL = OUTPUT_DIR / "images" / "val"
OUT_LABELS_TRAIN = OUTPUT_DIR / "labels" / "train"
OUT_LABELS_VAL = OUTPUT_DIR / "labels" / "val"
OUT_TEST_IMAGES = OUTPUT_DIR / "test" / "images"
OUT_TEST_LABELS = OUTPUT_DIR / "test" / "labels"

OUTPUT_DATA_YAML = OUTPUT_DIR / "data.yaml"
OUTPUT_SUMMARY_JSON = OUTPUT_DIR / "split_summary.json"
OUTPUT_CLASSES_FILE = OUTPUT_DIR / "classes.txt"

# ============================================================
# SPLIT SETTINGS
# ============================================================

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

RANDOM_SEED = 42
CLEAR_OUTPUT_ON_RUN = True

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

# Public standardized merged class name
STANDARDIZED_CLASS_NAME = "pedestrian"


def ensure_ratios_valid() -> None:
    total = TRAIN_RATIO + VAL_RATIO + TEST_RATIO
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Split ratios must sum to 1.0, got {total}")


def get_image_files(images_dir: Path):
    if not images_dir.exists():
        raise FileNotFoundError(f"Missing source image dir: {images_dir}")

    files = [
        p for p in images_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    files.sort(key=lambda p: p.name)
    return files


def matching_label_path(image_path: Path) -> Path:
    return SOURCE_LABELS_DIR / f"{image_path.stem}.txt"


def safe_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_data_yaml() -> None:
    text = (
        "path: .\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: test/images\n"
        "\n"
        "names:\n"
        f"  0: {STANDARDIZED_CLASS_NAME}\n"
    )
    OUTPUT_DATA_YAML.write_text(text, encoding="utf-8")


def write_classes_file() -> None:
    OUTPUT_CLASSES_FILE.write_text(f"{STANDARDIZED_CLASS_NAME}\n", encoding="utf-8")


def main() -> None:
    ensure_ratios_valid()

    if not SOURCE_IMAGES_DIR.exists():
        raise FileNotFoundError(f"Source images folder not found: {SOURCE_IMAGES_DIR}")
    if not SOURCE_LABELS_DIR.exists():
        raise FileNotFoundError(f"Source labels folder not found: {SOURCE_LABELS_DIR}")

    if CLEAR_OUTPUT_ON_RUN and OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    OUT_IMAGES_TRAIN.mkdir(parents=True, exist_ok=True)
    OUT_IMAGES_VAL.mkdir(parents=True, exist_ok=True)
    OUT_LABELS_TRAIN.mkdir(parents=True, exist_ok=True)
    OUT_LABELS_VAL.mkdir(parents=True, exist_ok=True)
    OUT_TEST_IMAGES.mkdir(parents=True, exist_ok=True)
    OUT_TEST_LABELS.mkdir(parents=True, exist_ok=True)

    image_files = get_image_files(SOURCE_IMAGES_DIR)
    total_images = len(image_files)

    if total_images == 0:
        raise RuntimeError("No source images found in filtered_yolo/images")

    rng = random.Random(RANDOM_SEED)
    shuffled = list(image_files)
    rng.shuffle(shuffled)

    n_train = int(total_images * TRAIN_RATIO)
    n_val = int(total_images * VAL_RATIO)
    n_test = total_images - n_train - n_val

    train_files = shuffled[:n_train]
    val_files = shuffled[n_train:n_train + n_val]
    test_files = shuffled[n_train + n_val:]

    def copy_split(files, out_img_dir: Path, out_lbl_dir: Path) -> dict:
        copied_images = 0
        copied_labels = 0
        missing_labels = 0

        for img_path in files:
            lbl_path = matching_label_path(img_path)

            safe_copy(img_path, out_img_dir / img_path.name)
            copied_images += 1

            if lbl_path.exists():
                safe_copy(lbl_path, out_lbl_dir / lbl_path.name)
                copied_labels += 1
            else:
                # Create empty YOLO label file if missing
                (out_lbl_dir / f"{img_path.stem}.txt").write_text("", encoding="utf-8")
                missing_labels += 1

        return {
            "images": copied_images,
            "labels": copied_labels,
            "missing_labels_created_empty": missing_labels,
        }

    train_stats = copy_split(train_files, OUT_IMAGES_TRAIN, OUT_LABELS_TRAIN)
    val_stats = copy_split(val_files, OUT_IMAGES_VAL, OUT_LABELS_VAL)
    test_stats = copy_split(test_files, OUT_TEST_IMAGES, OUT_TEST_LABELS)

    write_classes_file()
    write_data_yaml()

    summary = {
        "source_yolo_dir": str(SOURCE_YOLO_DIR),
        "output_dir": str(OUTPUT_DIR),
        "random_seed": RANDOM_SEED,
        "ratios": {
            "train": TRAIN_RATIO,
            "val": VAL_RATIO,
            "test": TEST_RATIO,
        },
        "counts": {
            "total_images": total_images,
            "train": len(train_files),
            "val": len(val_files),
            "test": len(test_files),
        },
        "train_stats": train_stats,
        "val_stats": val_stats,
        "test_stats": test_stats,
        "standardized_class_name": STANDARDIZED_CLASS_NAME,
        "notes": [
            "This script creates a local authorized YOLO split structure from processed/filtered_yolo.",
            "It does not publish or redistribute Cityscapes-derived images through the public repository."
        ]
    }

    OUTPUT_SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Done.")
    print("Source YOLO folder:", SOURCE_YOLO_DIR)
    print("Output Train_Data folder:", OUTPUT_DIR)
    print("")
    print("Counts:")
    print("  Total:", total_images)
    print("  Train:", len(train_files))
    print("  Val:", len(val_files))
    print("  Test:", len(test_files))
    print("")
    print("Files written:")
    print(" ", OUTPUT_DATA_YAML)
    print(" ", OUTPUT_SUMMARY_JSON)
    print(" ", OUTPUT_CLASSES_FILE)


if __name__ == "__main__":
    main()