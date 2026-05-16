from __future__ import annotations

from pathlib import Path
import csv
import re


# ============================================================
# EDIT THIS PATH
# Point this to your LOCAL Cityscapes-derived YOLO dataset root.
#
# Expected layout:
#   Train_Data/
#       images/train
#       images/val
#       labels/train
#       labels/val
#       test/images
#       test/labels
# ============================================================

LOCAL_DATASET_ROOT = Path(r"C:\Users\richm\Downloads\Cityscapes\processed\Train_Data")


# ============================================================
# FIXED PUBLIC METADATA DEFAULTS
# ============================================================

PUBLIC_CLASS_ID = 0
PUBLIC_CLASS_NAME = "pedestrian"

DETECTOR_NAME = "YOLOv5x"
DETECTOR_CONFIDENCE_RULE = "> 0.8"
MIN_OBJECT_SIZE_RULE = "70x32"

CROP_SIZE = "256x256"
SOURCE_WIDTH = 2048
SOURCE_HEIGHT = 1024

PRIVACY_BLUR_PRESENT = "yes"
OCCLUSION_EXPECTED = "yes"
GROUPING_EXPECTED = "yes"

FILTER_STAGE = "post_stage_03_yolo"


def count_nonempty_lines(txt_path: Path) -> int:
    if not txt_path.exists():
        return 0
    with txt_path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def source_image_id_from_sample_id(sample_id: str) -> str:
    """
    Script 01 wrote crop images like:
        frankfurt_000000_000294_leftImg8bit_crop_123.jpg

    We strip the trailing `_crop_<number>` to recover the source-image ID.
    """
    return re.sub(r"_crop_\d+$", "", sample_id)


def iter_split_files(root: Path):
    split_configs = [
        {
            "split": "train",
            "image_dir": root / "images" / "train",
            "label_dir": root / "labels" / "train",
        },
        {
            "split": "val",
            "image_dir": root / "images" / "val",
            "label_dir": root / "labels" / "val",
        },
        {
            "split": "test",
            "image_dir": root / "test" / "images",
            "label_dir": root / "test" / "labels",
        },
    ]

    for cfg in split_configs:
        image_dir = cfg["image_dir"]
        label_dir = cfg["label_dir"]
        split = cfg["split"]

        if not image_dir.exists():
            print(f"Warning: missing image dir for split '{split}': {image_dir}")
            continue

        images = sorted(
            [
                p for p in image_dir.iterdir()
                if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
            ]
        )

        for img_path in images:
            sample_id = img_path.stem
            label_path = label_dir / f"{sample_id}.txt"
            yield split, img_path, label_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    subset_root = repo_root / "cityscapes_pedestrian"
    manifest_path = subset_root / "manifests" / "cityscapes_pedestrian_manifest.csv"

    if not LOCAL_DATASET_ROOT.exists():
        raise FileNotFoundError(
            f"LOCAL_DATASET_ROOT does not exist: {LOCAL_DATASET_ROOT}"
        )

    rows = []

    for split, img_path, label_path in iter_split_files(LOCAL_DATASET_ROOT):
        sample_id = img_path.stem
        source_image_id = source_image_id_from_sample_id(sample_id)
        num_boxes = count_nonempty_lines(label_path)

        rows.append(
            {
                "sample_id": sample_id,
                "source_image_id": source_image_id,
                "split": split,
                "class_id": PUBLIC_CLASS_ID,
                "class_name": PUBLIC_CLASS_NAME,
                "num_boxes": num_boxes,
                "detector_name": DETECTOR_NAME,
                "detector_confidence_rule": DETECTOR_CONFIDENCE_RULE,
                "min_object_size_rule": MIN_OBJECT_SIZE_RULE,
                "crop_size": CROP_SIZE,
                "source_width": SOURCE_WIDTH,
                "source_height": SOURCE_HEIGHT,
                "privacy_blur_present": PRIVACY_BLUR_PRESENT,
                "occlusion_expected": OCCLUSION_EXPECTED,
                "grouping_expected": GROUPING_EXPECTED,
                "derived_artifact_relpath": "",
                "annotation_relpath": "",
                "filter_stage": FILTER_STAGE,
                "notes": "Public non-image record generated from local authorized YOLO split"
            }
        )

    fieldnames = [
        "sample_id",
        "source_image_id",
        "split",
        "class_id",
        "class_name",
        "num_boxes",
        "detector_name",
        "detector_confidence_rule",
        "min_object_size_rule",
        "crop_size",
        "source_width",
        "source_height",
        "privacy_blur_present",
        "occlusion_expected",
        "grouping_expected",
        "derived_artifact_relpath",
        "annotation_relpath",
        "filter_stage",
        "notes",
    ]

    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    train_count = sum(1 for r in rows if r["split"] == "train")
    val_count = sum(1 for r in rows if r["split"] == "val")
    test_count = sum(1 for r in rows if r["split"] == "test")

    print("Cityscapes public manifest written:")
    print(manifest_path)
    print("")
    print("Total rows:", len(rows))
    print("Train:", train_count)
    print("Val:", val_count)
    print("Test:", test_count)


if __name__ == "__main__":
    main()