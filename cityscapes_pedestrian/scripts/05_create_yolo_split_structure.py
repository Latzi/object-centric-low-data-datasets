from __future__ import annotations

import argparse
import json
import os
import random
import shutil
from pathlib import Path


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_TRAIN_RATIO = 0.70
DEFAULT_VAL_RATIO = 0.15
DEFAULT_TEST_RATIO = 0.15

DEFAULT_RANDOM_SEED = 42
DEFAULT_CLEAR_OUTPUT_ON_RUN = True

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

DEFAULT_STANDARDIZED_CLASS_NAME = "pedestrian"


# ============================================================
# ARGUMENTS
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a YOLO train/validation/test folder structure from the "
            "local Cityscapes--Pedestrian filtered_yolo output."
        )
    )

    parser.add_argument(
        "--processed-dir",
        default=os.environ.get("CITYSCAPES_PROCESSED_DIR"),
        help=(
            "Path to the local processed Cityscapes--Pedestrian folder. "
            "Default source/output paths are derived from this folder. "
            "You may also set CITYSCAPES_PROCESSED_DIR."
        ),
    )

    parser.add_argument(
        "--source-yolo-dir",
        default=os.environ.get("CITYSCAPES_FILTERED_YOLO_DIR"),
        help=(
            "Path to the local filtered_yolo folder produced by script 03. "
            "Expected contents: images/, labels/. "
            "Default: PROCESSED_DIR/filtered_yolo. "
            "You may also set CITYSCAPES_FILTERED_YOLO_DIR."
        ),
    )

    parser.add_argument(
        "--output-dir",
        default=os.environ.get("CITYSCAPES_TRAIN_DATA_DIR"),
        help=(
            "Output folder for the YOLO Train_Data structure. "
            "Default: PROCESSED_DIR/Train_Data. "
            "You may also set CITYSCAPES_TRAIN_DATA_DIR."
        ),
    )

    parser.add_argument(
        "--train-ratio",
        type=float,
        default=DEFAULT_TRAIN_RATIO,
        help="Training split ratio. Default: 0.70.",
    )

    parser.add_argument(
        "--val-ratio",
        type=float,
        default=DEFAULT_VAL_RATIO,
        help="Validation split ratio. Default: 0.15.",
    )

    parser.add_argument(
        "--test-ratio",
        type=float,
        default=DEFAULT_TEST_RATIO,
        help="Test split ratio. Default: 0.15.",
    )

    parser.add_argument(
        "--random-seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
        help="Random seed used for splitting. Default: 42.",
    )

    parser.add_argument(
        "--standardized-class-name",
        default=DEFAULT_STANDARDIZED_CLASS_NAME,
        help="Class name written to classes.txt and data.yaml. Default: pedestrian.",
    )

    parser.add_argument(
        "--clear-output",
        dest="clear_output_on_run",
        action="store_true",
        default=DEFAULT_CLEAR_OUTPUT_ON_RUN,
        help="Delete the old output folder before writing. This is the default.",
    )

    parser.add_argument(
        "--no-clear-output",
        dest="clear_output_on_run",
        action="store_false",
        help="Do not delete the old output folder before writing.",
    )

    return parser.parse_args()


# ============================================================
# PATH RESOLUTION AND VALIDATION
# ============================================================

def resolve_paths(args: argparse.Namespace) -> dict:
    processed_dir = (
        Path(args.processed_dir).expanduser().resolve()
        if args.processed_dir
        else None
    )

    if args.source_yolo_dir:
        source_yolo_dir = Path(args.source_yolo_dir).expanduser().resolve()
    else:
        if processed_dir is None:
            raise RuntimeError(
                "No source YOLO directory was provided. Pass --source-yolo-dir, "
                "or pass --processed-dir, or set CITYSCAPES_FILTERED_YOLO_DIR "
                "or CITYSCAPES_PROCESSED_DIR."
            )

        source_yolo_dir = processed_dir / "filtered_yolo"

    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        if processed_dir is not None:
            output_dir = processed_dir / "Train_Data"
        else:
            output_dir = source_yolo_dir.parent / "Train_Data"

    paths = {
        "processed_dir": processed_dir,
        "source_yolo_dir": source_yolo_dir,
        "source_images_dir": source_yolo_dir / "images",
        "source_labels_dir": source_yolo_dir / "labels",
        "output_dir": output_dir,
        "out_images_train": output_dir / "images" / "train",
        "out_images_val": output_dir / "images" / "val",
        "out_labels_train": output_dir / "labels" / "train",
        "out_labels_val": output_dir / "labels" / "val",
        "out_test_images": output_dir / "test" / "images",
        "out_test_labels": output_dir / "test" / "labels",
        "output_data_yaml": output_dir / "data.yaml",
        "output_summary_json": output_dir / "split_summary.json",
        "output_classes_file": output_dir / "classes.txt",
    }

    return paths


def ensure_ratios_valid(train_ratio: float, val_ratio: float, test_ratio: float) -> None:
    total = train_ratio + val_ratio + test_ratio

    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Split ratios must sum to 1.0, got {total}")


def validate_inputs(paths: dict) -> None:
    source_images_dir = paths["source_images_dir"]
    source_labels_dir = paths["source_labels_dir"]

    if not source_images_dir.exists():
        raise FileNotFoundError(f"Source images folder not found: {source_images_dir}")

    if not source_labels_dir.exists():
        raise FileNotFoundError(f"Source labels folder not found: {source_labels_dir}")


# ============================================================
# HELPERS
# ============================================================

def get_image_files(images_dir: Path):
    files = [
        path for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    files.sort(key=lambda path: path.name)
    return files


def matching_label_path(image_path: Path, source_labels_dir: Path) -> Path:
    return source_labels_dir / f"{image_path.stem}.txt"


def safe_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_data_yaml(
    output_data_yaml: Path,
    standardized_class_name: str,
) -> None:
    text = (
        "path: .\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: test/images\n"
        "\n"
        "names:\n"
        f"  0: {standardized_class_name}\n"
    )

    output_data_yaml.write_text(text, encoding="utf-8")


def write_classes_file(
    output_classes_file: Path,
    standardized_class_name: str,
) -> None:
    output_classes_file.write_text(
        f"{standardized_class_name}\n",
        encoding="utf-8",
    )


def copy_split(
    files,
    out_img_dir: Path,
    out_lbl_dir: Path,
    source_labels_dir: Path,
) -> dict:
    copied_images = 0
    copied_labels = 0
    missing_labels = 0

    for img_path in files:
        lbl_path = matching_label_path(img_path, source_labels_dir)

        safe_copy(img_path, out_img_dir / img_path.name)
        copied_images += 1

        if lbl_path.exists():
            safe_copy(lbl_path, out_lbl_dir / lbl_path.name)
            copied_labels += 1
        else:
            # Create an empty YOLO label file if the source label is missing.
            (out_lbl_dir / f"{img_path.stem}.txt").write_text("", encoding="utf-8")
            missing_labels += 1

    return {
        "images": copied_images,
        "labels": copied_labels,
        "missing_labels_created_empty": missing_labels,
    }


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    args = parse_args()
    paths = resolve_paths(args)

    ensure_ratios_valid(
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
    )

    validate_inputs(paths)

    source_yolo_dir = paths["source_yolo_dir"]
    source_images_dir = paths["source_images_dir"]
    source_labels_dir = paths["source_labels_dir"]
    output_dir = paths["output_dir"]

    print("Cityscapes--Pedestrian YOLO split creation")
    print("==========================================")
    print(f"Source YOLO folder:   {source_yolo_dir}")
    print(f"Source images folder: {source_images_dir}")
    print(f"Source labels folder: {source_labels_dir}")
    print(f"Output Train_Data:    {output_dir}")
    print(f"Train ratio:          {args.train_ratio}")
    print(f"Val ratio:            {args.val_ratio}")
    print(f"Test ratio:           {args.test_ratio}")
    print(f"Random seed:          {args.random_seed}")
    print(f"Class name:           {args.standardized_class_name}")
    print(f"Clear output:         {args.clear_output_on_run}")

    if args.clear_output_on_run and output_dir.exists():
        shutil.rmtree(output_dir)

    paths["out_images_train"].mkdir(parents=True, exist_ok=True)
    paths["out_images_val"].mkdir(parents=True, exist_ok=True)
    paths["out_labels_train"].mkdir(parents=True, exist_ok=True)
    paths["out_labels_val"].mkdir(parents=True, exist_ok=True)
    paths["out_test_images"].mkdir(parents=True, exist_ok=True)
    paths["out_test_labels"].mkdir(parents=True, exist_ok=True)

    image_files = get_image_files(source_images_dir)
    total_images = len(image_files)

    if total_images == 0:
        raise RuntimeError(f"No source images found in {source_images_dir}")

    rng = random.Random(args.random_seed)

    shuffled = list(image_files)
    rng.shuffle(shuffled)

    n_train = int(total_images * args.train_ratio)
    n_val = int(total_images * args.val_ratio)
    n_test = total_images - n_train - n_val

    train_files = shuffled[:n_train]
    val_files = shuffled[n_train:n_train + n_val]
    test_files = shuffled[n_train + n_val:]

    train_stats = copy_split(
        files=train_files,
        out_img_dir=paths["out_images_train"],
        out_lbl_dir=paths["out_labels_train"],
        source_labels_dir=source_labels_dir,
    )

    val_stats = copy_split(
        files=val_files,
        out_img_dir=paths["out_images_val"],
        out_lbl_dir=paths["out_labels_val"],
        source_labels_dir=source_labels_dir,
    )

    test_stats = copy_split(
        files=test_files,
        out_img_dir=paths["out_test_images"],
        out_lbl_dir=paths["out_test_labels"],
        source_labels_dir=source_labels_dir,
    )

    write_classes_file(
        output_classes_file=paths["output_classes_file"],
        standardized_class_name=args.standardized_class_name,
    )

    write_data_yaml(
        output_data_yaml=paths["output_data_yaml"],
        standardized_class_name=args.standardized_class_name,
    )

    summary = {
        "source_yolo_dir": str(source_yolo_dir),
        "output_dir": str(output_dir),
        "random_seed": args.random_seed,
        "ratios": {
            "train": args.train_ratio,
            "val": args.val_ratio,
            "test": args.test_ratio,
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
        "standardized_class_name": args.standardized_class_name,
        "notes": [
            "This script creates a local authorized YOLO split structure from filtered_yolo.",
            "It does not publish or redistribute Cityscapes-derived images through the public repository.",
        ],
    }

    paths["output_summary_json"].write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("")
    print("Done.")
    print(f"Source YOLO folder: {source_yolo_dir}")
    print(f"Output Train_Data folder: {output_dir}")
    print("")
    print("Counts:")
    print(f"  Total: {total_images}")
    print(f"  Train: {len(train_files)}")
    print(f"  Val:   {len(val_files)}")
    print(f"  Test:  {len(test_files)}")
    print("")
    print("Files written:")
    print(f"  {paths['output_data_yaml']}")
    print(f"  {paths['output_summary_json']}")
    print(f"  {paths['output_classes_file']}")


if __name__ == "__main__":
    main()