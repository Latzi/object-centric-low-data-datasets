from __future__ import annotations

from pathlib import Path
import csv
import re
import cv2


# ============================================================
# LOCAL DATA-PC PATHS
# ============================================================

# Local cropped YOLO subset produced by step 02 on the DATA PC
LOCAL_CROPPED_ROOT = Path(r"C:\Users\richm\Downloads\COCO_Dataset\YOLO_pottedplant_cropped")

# Local full-image YOLO subset produced by step 01 on the DATA PC
LOCAL_FULL_YOLO_ROOT = Path(r"C:\Users\richm\Downloads\COCO_Dataset\YOLO_pottedplant")

# Output CSV written on the DATA PC
OUTPUT_MANIFEST_PATH = Path(r"C:\Users\richm\Downloads\COCO_Dataset\coco_pottedplant_manifest.csv")


# ============================================================
# FIXED PUBLIC METADATA DEFAULTS
# ============================================================

PUBLIC_CLASS_ID = 0
PUBLIC_CLASS_NAME = "potted_plant"

SOURCE_CATEGORY_ID = ""
SOURCE_CATEGORY_NAME = "potted plant"

CROP_SIZE = "256x256"
SMALL_BOX_FILTER_RULE = "min_w>=12,min_h>=12"
RANDOM_OFFSET_EXPECTED = "yes"
CONTEXT_VARIABILITY_EXPECTED = "yes"
MASK_EXPECTED = "no"

FILTER_STAGE = "post_stage_02_cropped_yolo"


# ============================================================
# HELPERS
# ============================================================

def count_nonempty_lines(txt_path: Path) -> int:
    if not txt_path.exists():
        return 0
    with txt_path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def parse_sample_id(sample_id: str):
    """
    Expected cropped filename stem from step 02:

        <source_image_id>_inst0003_crop_12_34

    Returns:
        source_image_id, selected_instance_index

    If parsing fails, selected_instance_index becomes blank.
    """
    m = re.match(r"^(?P<source>.+)_inst(?P<idx>\d+)_crop_(?P<x>-?\d+)_(?P<y>-?\d+)$", sample_id)
    if not m:
        return sample_id, ""

    source_image_id = m.group("source")
    selected_instance_index = int(m.group("idx"))
    return source_image_id, selected_instance_index


def parse_yolo_line(line: str):
    line = line.strip()
    if not line:
        return None

    parts = line.split()
    if len(parts) < 5:
        return None

    try:
        class_id = int(float(parts[0]))
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        return {
            "class_id": class_id,
            "x_center": x_center,
            "y_center": y_center,
            "width": width,
            "height": height,
        }
    except Exception:
        return None


def get_source_image_size(split: str, source_image_id: str):
    """
    Try to recover the original full-image dimensions from the full-image YOLO subset.
    """
    for ext in [".jpg", ".jpeg", ".png"]:
        img_path = LOCAL_FULL_YOLO_ROOT / "images" / split / f"{source_image_id}{ext}"
        if img_path.exists():
            img = cv2.imread(str(img_path))
            if img is not None:
                h, w = img.shape[:2]
                return w, h
    return "", ""


def get_selected_instance_box_size(split: str, source_image_id: str, selected_instance_index):
    """
    Recover the selected source-instance bbox width/height in pixels by reading
    the corresponding source full-image YOLO label file.

    This assumes the cropped filename's `instXXXX` index matches the annotation
    line index used in step 02.
    """
    if selected_instance_index == "":
        return "", ""

    label_path = LOCAL_FULL_YOLO_ROOT / "labels" / split / f"{source_image_id}.txt"
    if not label_path.exists():
        return "", ""

    lines = [ln.strip() for ln in label_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if selected_instance_index < 0 or selected_instance_index >= len(lines):
        return "", ""

    ann = parse_yolo_line(lines[selected_instance_index])
    if ann is None:
        return "", ""

    src_w, src_h = get_source_image_size(split, source_image_id)
    if src_w == "" or src_h == "":
        return "", ""

    bw_pixels = round(ann["width"] * src_w, 2)
    bh_pixels = round(ann["height"] * src_h, 2)
    return bw_pixels, bh_pixels


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


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    if not LOCAL_CROPPED_ROOT.exists():
        raise FileNotFoundError(f"LOCAL_CROPPED_ROOT does not exist: {LOCAL_CROPPED_ROOT}")

    if not LOCAL_FULL_YOLO_ROOT.exists():
        raise FileNotFoundError(f"LOCAL_FULL_YOLO_ROOT does not exist: {LOCAL_FULL_YOLO_ROOT}")

    rows = []

    for split, img_path, label_path in iter_split_files(LOCAL_CROPPED_ROOT):
        sample_id = img_path.stem
        source_image_id, selected_instance_index = parse_sample_id(sample_id)
        num_boxes = count_nonempty_lines(label_path)

        source_width, source_height = get_source_image_size(split, source_image_id)
        selected_bbox_w, selected_bbox_h = get_selected_instance_box_size(
            split, source_image_id, selected_instance_index
        )

        rows.append(
            {
                "sample_id": sample_id,
                "source_image_id": source_image_id,
                "selected_instance_index": selected_instance_index,
                "source_annotation_id": "",
                "source_category_id": SOURCE_CATEGORY_ID,
                "source_category_name": SOURCE_CATEGORY_NAME,
                "split": split,
                "class_id": PUBLIC_CLASS_ID,
                "class_name": PUBLIC_CLASS_NAME,
                "num_boxes": num_boxes,
                "crop_size": CROP_SIZE,
                "source_width": source_width,
                "source_height": source_height,
                "selected_instance_bbox_width": selected_bbox_w,
                "selected_instance_bbox_height": selected_bbox_h,
                "small_box_filter_rule": SMALL_BOX_FILTER_RULE,
                "random_offset_expected": RANDOM_OFFSET_EXPECTED,
                "context_variability_expected": CONTEXT_VARIABILITY_EXPECTED,
                "mask_expected": MASK_EXPECTED,
                "derived_artifact_relpath": "",
                "annotation_relpath": "",
                "filter_stage": FILTER_STAGE,
                "notes": "Public metadata record generated from local cropped YOLO subset"
            }
        )

    fieldnames = [
        "sample_id",
        "source_image_id",
        "selected_instance_index",
        "source_annotation_id",
        "source_category_id",
        "source_category_name",
        "split",
        "class_id",
        "class_name",
        "num_boxes",
        "crop_size",
        "source_width",
        "source_height",
        "selected_instance_bbox_width",
        "selected_instance_bbox_height",
        "small_box_filter_rule",
        "random_offset_expected",
        "context_variability_expected",
        "mask_expected",
        "derived_artifact_relpath",
        "annotation_relpath",
        "filter_stage",
        "notes",
    ]

    OUTPUT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_MANIFEST_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    train_count = sum(1 for r in rows if r["split"] == "train")
    val_count = sum(1 for r in rows if r["split"] == "val")

    print("COCO public manifest written:")
    print(OUTPUT_MANIFEST_PATH)
    print("")
    print("Total rows:", len(rows))
    print("Train:", train_count)
    print("Val:", val_count)


if __name__ == "__main__":
    main()