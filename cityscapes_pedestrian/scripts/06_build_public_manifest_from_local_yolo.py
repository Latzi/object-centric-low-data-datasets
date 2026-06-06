from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path


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

DEFAULT_SPLITS = ["train", "val", "test"]


# ============================================================
# ARGUMENTS
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the public Cityscapes--Pedestrian manifest from a local "
            "authorized YOLO Train_Data folder."
        )
    )

    parser.add_argument(
        "--local-dataset-root",
        default=os.environ.get("CITYSCAPES_LOCAL_YOLO_ROOT"),
        help=(
            "Path to the local Cityscapes--Pedestrian YOLO Train_Data folder. "
            "Expected layout: images/train, images/val, labels/train, labels/val, "
            "test/images, test/labels. You may also set CITYSCAPES_LOCAL_YOLO_ROOT."
        ),
    )

    parser.add_argument(
        "--output-manifest-path",
        default=os.environ.get("CITYSCAPES_OUTPUT_MANIFEST_PATH"),
        help=(
            "Output path for the generated public manifest CSV. "
            "Default: repo/cityscapes_pedestrian/manifests/"
            "cityscapes_pedestrian_manifest.csv. You may also set "
            "CITYSCAPES_OUTPUT_MANIFEST_PATH."
        ),
    )

    parser.add_argument(
        "--splits",
        nargs="+",
        default=DEFAULT_SPLITS,
        choices=["train", "val", "test"],
        help="Splits to include in the manifest. Default: train val test.",
    )

    parser.add_argument(
        "--public-class-id",
        type=int,
        default=PUBLIC_CLASS_ID,
        help="Public class ID written to the manifest. Default: 0.",
    )

    parser.add_argument(
        "--public-class-name",
        default=PUBLIC_CLASS_NAME,
        help="Public class name written to the manifest. Default: pedestrian.",
    )

    parser.add_argument(
        "--detector-name",
        default=DETECTOR_NAME,
        help="Public metadata value for detector/source name. Default: YOLOv5x.",
    )

    parser.add_argument(
        "--detector-confidence-rule",
        default=DETECTOR_CONFIDENCE_RULE,
        help="Public metadata value for detector confidence rule. Default: > 0.8.",
    )

    parser.add_argument(
        "--min-object-size-rule",
        default=MIN_OBJECT_SIZE_RULE,
        help="Public metadata value for minimum object size rule. Default: 70x32.",
    )

    parser.add_argument(
        "--crop-size",
        default=CROP_SIZE,
        help="Public metadata value for crop size. Default: 256x256.",
    )

    parser.add_argument(
        "--source-width",
        type=int,
        default=SOURCE_WIDTH,
        help="Public metadata value for source image width. Default: 2048.",
    )

    parser.add_argument(
        "--source-height",
        type=int,
        default=SOURCE_HEIGHT,
        help="Public metadata value for source image height. Default: 1024.",
    )

    parser.add_argument(
        "--privacy-blur-present",
        default=PRIVACY_BLUR_PRESENT,
        choices=["yes", "no"],
        help="Whether privacy blur is expected in the source images. Default: yes.",
    )

    parser.add_argument(
        "--occlusion-expected",
        default=OCCLUSION_EXPECTED,
        choices=["yes", "no"],
        help="Whether occlusion is expected in this subset. Default: yes.",
    )

    parser.add_argument(
        "--grouping-expected",
        default=GROUPING_EXPECTED,
        choices=["yes", "no"],
        help="Whether group scenes are expected in this subset. Default: yes.",
    )

    parser.add_argument(
        "--filter-stage",
        default=FILTER_STAGE,
        help="Public metadata value for filter stage. Default: post_stage_03_yolo.",
    )

    return parser.parse_args()


# ============================================================
# PATH RESOLUTION AND VALIDATION
# ============================================================

def resolve_paths(args: argparse.Namespace) -> dict:
    if not args.local_dataset_root:
        raise RuntimeError(
            "Local dataset root was not provided. Pass --local-dataset-root "
            "or set CITYSCAPES_LOCAL_YOLO_ROOT."
        )

    local_dataset_root = Path(args.local_dataset_root).expanduser().resolve()

    if args.output_manifest_path:
        manifest_path = Path(args.output_manifest_path).expanduser().resolve()
    else:
        repo_root = Path(__file__).resolve().parents[2]
        subset_root = repo_root / "cityscapes_pedestrian"
        manifest_path = subset_root / "manifests" / "cityscapes_pedestrian_manifest.csv"

    return {
        "local_dataset_root": local_dataset_root,
        "manifest_path": manifest_path,
    }


def validate_inputs(local_dataset_root: Path, splits) -> None:
    if not local_dataset_root.exists():
        raise FileNotFoundError(
            f"Local dataset root does not exist: {local_dataset_root}"
        )

    for split in splits:
        image_dir, label_dir = get_split_dirs(local_dataset_root, split)

        if not image_dir.exists():
            raise FileNotFoundError(
                f"Image directory for split '{split}' does not exist: {image_dir}"
            )

        if not label_dir.exists():
            raise FileNotFoundError(
                f"Label directory for split '{split}' does not exist: {label_dir}"
            )


# ============================================================
# HELPERS
# ============================================================

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


def get_split_dirs(root: Path, split: str):
    if split == "test":
        image_dir = root / "test" / "images"
        label_dir = root / "test" / "labels"
    else:
        image_dir = root / "images" / split
        label_dir = root / "labels" / split

    return image_dir, label_dir


def iter_split_files(root: Path, splits):
    for split in splits:
        image_dir, label_dir = get_split_dirs(root, split)

        images = sorted(
            [
                path for path in image_dir.iterdir()
                if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
            ]
        )

        for img_path in images:
            sample_id = img_path.stem
            label_path = label_dir / f"{sample_id}.txt"
            yield split, img_path, label_path


def get_manifest_fieldnames():
    return [
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


def build_manifest_rows(local_dataset_root: Path, args: argparse.Namespace):
    rows = []

    for split, img_path, label_path in iter_split_files(local_dataset_root, args.splits):
        sample_id = img_path.stem
        source_image_id = source_image_id_from_sample_id(sample_id)
        num_boxes = count_nonempty_lines(label_path)

        rows.append(
            {
                "sample_id": sample_id,
                "source_image_id": source_image_id,
                "split": split,
                "class_id": args.public_class_id,
                "class_name": args.public_class_name,
                "num_boxes": num_boxes,
                "detector_name": args.detector_name,
                "detector_confidence_rule": args.detector_confidence_rule,
                "min_object_size_rule": args.min_object_size_rule,
                "crop_size": args.crop_size,
                "source_width": args.source_width,
                "source_height": args.source_height,
                "privacy_blur_present": args.privacy_blur_present,
                "occlusion_expected": args.occlusion_expected,
                "grouping_expected": args.grouping_expected,
                "derived_artifact_relpath": "",
                "annotation_relpath": "",
                "filter_stage": args.filter_stage,
                "notes": (
                    "Public non-image record generated from local authorized YOLO split"
                ),
            }
        )

    return rows


def write_manifest(manifest_path: Path, rows) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=get_manifest_fieldnames())
        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    args = parse_args()
    paths = resolve_paths(args)

    local_dataset_root = paths["local_dataset_root"]
    manifest_path = paths["manifest_path"]

    validate_inputs(local_dataset_root, args.splits)

    print("Cityscapes--Pedestrian public manifest builder")
    print("==============================================")
    print(f"Local dataset root: {local_dataset_root}")
    print(f"Output manifest:    {manifest_path}")
    print(f"Splits:             {args.splits}")

    rows = build_manifest_rows(local_dataset_root, args)
    write_manifest(manifest_path, rows)

    train_count = sum(1 for row in rows if row["split"] == "train")
    val_count = sum(1 for row in rows if row["split"] == "val")
    test_count = sum(1 for row in rows if row["split"] == "test")

    print("")
    print("Cityscapes public manifest written:")
    print(manifest_path)
    print("")
    print("Total rows:", len(rows))
    print("Train:", train_count)
    print("Val:", val_count)
    print("Test:", test_count)


if __name__ == "__main__":
    main()