import argparse
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_YOLO_CLASS_MODE = "person_related_single_class"

DEFAULT_PERSON_RELATED_LABELS = [
    "pedestrian",
    "sitting person",
    "person group",
    "person (other)",
    "rider",
    "person",
    "persongroup",
    "ridergroup",
]

DEFAULT_SINGLE_PERSON_CLASS_NAME = "person"

DEFAULT_CLEAR_YOLO_OUTPUT_ON_RUN = True
DEFAULT_COPY_IMAGES_TO_YOLO_FOLDER = True
DEFAULT_CREATE_EMPTY_LABEL_FILES = True

DEFAULT_CLIP_BOXES_TO_IMAGE = True
DEFAULT_MIN_BOX_WIDTH_PIXELS = 1.0
DEFAULT_MIN_BOX_HEIGHT_PIXELS = 1.0
DEFAULT_YOLO_DECIMALS = 6


# ============================================================
# ARGUMENTS
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Create YOLO-format annotations from filtered Cityscapes--Pedestrian "
            "COCO-style crop annotations."
        )
    )

    parser.add_argument(
        "--processed-dir",
        default=os.environ.get("CITYSCAPES_PROCESSED_DIR"),
        help=(
            "Path to the local processed Cityscapes--Pedestrian folder. "
            "Default paths are derived from this folder. You may also set "
            "CITYSCAPES_PROCESSED_DIR."
        ),
    )

    parser.add_argument(
        "--filtered-dir",
        default=os.environ.get("CITYSCAPES_FILTERED_DIR"),
        help=(
            "Path to the filtered images folder created by script 02. "
            "Default: PROCESSED_DIR/filtered_images. You may also set "
            "CITYSCAPES_FILTERED_DIR."
        ),
    )

    parser.add_argument(
        "--filtered-images-dir",
        default=None,
        help=(
            "Optional explicit path to filtered images. "
            "Default: FILTERED_DIR."
        ),
    )

    parser.add_argument(
        "--filtered-annotations-file",
        default=None,
        help=(
            "Optional explicit path to filtered_annotations.json. "
            "Default: FILTERED_DIR/filtered_annotations.json."
        ),
    )

    parser.add_argument(
        "--yolo-output-dir",
        default=os.environ.get("CITYSCAPES_FILTERED_YOLO_DIR"),
        help=(
            "Output folder for the YOLO dataset. "
            "Default: PROCESSED_DIR/filtered_yolo. You may also set "
            "CITYSCAPES_FILTERED_YOLO_DIR."
        ),
    )

    parser.add_argument(
        "--clear-yolo-output",
        dest="clear_yolo_output_on_run",
        action="store_true",
        default=DEFAULT_CLEAR_YOLO_OUTPUT_ON_RUN,
        help="Delete the old YOLO output folder before writing. This is the default.",
    )

    parser.add_argument(
        "--no-clear-yolo-output",
        dest="clear_yolo_output_on_run",
        action="store_false",
        help="Do not delete the old YOLO output folder before writing.",
    )

    parser.add_argument(
        "--copy-images-to-yolo-folder",
        dest="copy_images_to_yolo_folder",
        action="store_true",
        default=DEFAULT_COPY_IMAGES_TO_YOLO_FOLDER,
        help="Copy filtered images into YOLO_OUTPUT_DIR/images. This is the default.",
    )

    parser.add_argument(
        "--no-copy-images-to-yolo-folder",
        dest="copy_images_to_yolo_folder",
        action="store_false",
        help="Do not copy images into the YOLO output folder.",
    )

    parser.add_argument(
        "--create-empty-label-files",
        dest="create_empty_label_files",
        action="store_true",
        default=DEFAULT_CREATE_EMPTY_LABEL_FILES,
        help="Create empty .txt labels for images with no kept boxes. This is the default.",
    )

    parser.add_argument(
        "--no-create-empty-label-files",
        dest="create_empty_label_files",
        action="store_false",
        help="Do not create empty .txt labels for images with no kept boxes.",
    )

    parser.add_argument(
        "--yolo-class-mode",
        choices=[
            "person_related_single_class",
            "all_categories",
            "person_related_multi_class",
        ],
        default=DEFAULT_YOLO_CLASS_MODE,
        help=(
            "YOLO class mapping mode. Default: person_related_single_class. "
            "Use all_categories to keep all COCO categories as separate YOLO classes."
        ),
    )

    parser.add_argument(
        "--single-person-class-name",
        default=DEFAULT_SINGLE_PERSON_CLASS_NAME,
        help=(
            "YOLO class name used for class 0 in person_related_single_class mode. "
            "Default: person."
        ),
    )

    parser.add_argument(
        "--clip-boxes-to-image",
        dest="clip_boxes_to_image",
        action="store_true",
        default=DEFAULT_CLIP_BOXES_TO_IMAGE,
        help="Clip boxes so they stay inside the image area. This is the default.",
    )

    parser.add_argument(
        "--no-clip-boxes-to-image",
        dest="clip_boxes_to_image",
        action="store_false",
        help="Do not clip boxes to the image area.",
    )

    parser.add_argument(
        "--min-box-width-pixels",
        type=float,
        default=DEFAULT_MIN_BOX_WIDTH_PIXELS,
        help="Ignore boxes narrower than this after clipping. Default: 1.0.",
    )

    parser.add_argument(
        "--min-box-height-pixels",
        type=float,
        default=DEFAULT_MIN_BOX_HEIGHT_PIXELS,
        help="Ignore boxes shorter than this after clipping. Default: 1.0.",
    )

    parser.add_argument(
        "--yolo-decimals",
        type=int,
        default=DEFAULT_YOLO_DECIMALS,
        help="Number of decimal places in YOLO label files. Default: 6.",
    )

    return parser.parse_args()


# ============================================================
# PATH RESOLUTION AND VALIDATION
# ============================================================

def resolve_paths(args):
    processed_dir = (
        Path(args.processed_dir).expanduser().resolve()
        if args.processed_dir
        else None
    )

    if args.filtered_dir:
        filtered_dir = Path(args.filtered_dir).expanduser().resolve()
    else:
        if processed_dir is None:
            raise RuntimeError(
                "No filtered directory was provided. Pass --filtered-dir, "
                "or pass --processed-dir, or set CITYSCAPES_PROCESSED_DIR."
            )
        filtered_dir = processed_dir / "filtered_images"

    if args.filtered_images_dir:
        filtered_images_dir = Path(args.filtered_images_dir).expanduser().resolve()
    else:
        filtered_images_dir = filtered_dir

    if args.filtered_annotations_file:
        filtered_annotations_file = (
            Path(args.filtered_annotations_file).expanduser().resolve()
        )
    else:
        filtered_annotations_file = filtered_dir / "filtered_annotations.json"

    if args.yolo_output_dir:
        yolo_output_dir = Path(args.yolo_output_dir).expanduser().resolve()
    else:
        if processed_dir is not None:
            yolo_output_dir = processed_dir / "filtered_yolo"
        else:
            yolo_output_dir = filtered_dir.parent / "filtered_yolo"

    return {
        "processed_dir": processed_dir,
        "filtered_dir": filtered_dir,
        "filtered_images_dir": filtered_images_dir,
        "filtered_annotations_file": filtered_annotations_file,
        "yolo_output_dir": yolo_output_dir,
        "yolo_images_dir": yolo_output_dir / "images",
        "yolo_labels_dir": yolo_output_dir / "labels",
        "yolo_classes_file": yolo_output_dir / "classes.txt",
        "yolo_data_yaml_file": yolo_output_dir / "data.yaml",
        "yolo_summary_file": yolo_output_dir / "conversion_summary.json",
    }


def validate_inputs(paths):
    filtered_images_dir = paths["filtered_images_dir"]
    filtered_annotations_file = paths["filtered_annotations_file"]

    if not filtered_images_dir.is_dir():
        raise FileNotFoundError(
            f"Filtered images directory does not exist: {filtered_images_dir}"
        )

    if not filtered_annotations_file.is_file():
        raise FileNotFoundError(
            f"Filtered annotations file does not exist: {filtered_annotations_file}"
        )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_label(label):
    """Normalize category names for matching."""
    return str(label).strip().lower()


def safe_int(value):
    """Try converting a value to int. Return None if not possible."""
    try:
        return int(value)
    except Exception:
        return None


def build_category_lookup(coco_data):
    """
    Build category_id -> category_name lookup.

    COCO annotations usually store:
        "category_id": 5

    while categories contain:
        {"id": 5, "name": "person"}
    """
    id_to_name = {}

    for cat in coco_data.get("categories", []):
        cat_id = cat.get("id")
        cat_name = cat.get("name", "")

        id_to_name[cat_id] = cat_name
        id_to_name[str(cat_id)] = cat_name

        cat_id_int = safe_int(cat_id)
        if cat_id_int is not None:
            id_to_name[cat_id_int] = cat_name

    return id_to_name


def get_annotation_label(ann, id_to_name):
    """
    Return readable category name for an annotation.

    Handles normal COCO:
        ann["category_id"] = 5

    Also handles non-standard cases where:
        ann["category_id"] = "person"
    """
    category_id = ann.get("category_id")

    if category_id in id_to_name:
        return id_to_name[category_id]

    category_id_str = str(category_id)
    if category_id_str in id_to_name:
        return id_to_name[category_id_str]

    category_id_int = safe_int(category_id)
    if category_id_int is not None and category_id_int in id_to_name:
        return id_to_name[category_id_int]

    return category_id_str


def category_sort_key(cat):
    """Stable sorting key for COCO-style categories."""
    cat_id = cat.get("id")
    cat_id_int = safe_int(cat_id)

    if cat_id_int is not None:
        return (0, cat_id_int)

    return (1, str(cat_id))


def build_yolo_class_mapping(coco_data, yolo_class_mode, single_person_class_name):
    """
    Build class names and label/category mappings for YOLO conversion.
    """
    categories = coco_data.get("categories", [])

    if yolo_class_mode == "person_related_single_class":
        class_names = [single_person_class_name]

        allowed_labels = {
            clean_label(label)
            for label in DEFAULT_PERSON_RELATED_LABELS
        }

        return {
            "class_names": class_names,
            "allowed_labels": allowed_labels,
            "label_to_yolo_id": None,
            "category_id_to_yolo_id": None,
        }

    if yolo_class_mode == "person_related_multi_class":
        class_names = list(DEFAULT_PERSON_RELATED_LABELS)

        label_to_yolo_id = {}
        for idx, name in enumerate(class_names):
            label_to_yolo_id[clean_label(name)] = idx

        return {
            "class_names": class_names,
            "allowed_labels": set(label_to_yolo_id.keys()),
            "label_to_yolo_id": label_to_yolo_id,
            "category_id_to_yolo_id": None,
        }

    if yolo_class_mode == "all_categories":
        sorted_categories = sorted(categories, key=category_sort_key)

        class_names = []
        category_id_to_yolo_id = {}
        label_to_yolo_id = {}

        for yolo_id, cat in enumerate(sorted_categories):
            cat_id = cat.get("id")
            cat_name = cat.get("name", "")

            class_names.append(cat_name)

            category_id_to_yolo_id[cat_id] = yolo_id
            category_id_to_yolo_id[str(cat_id)] = yolo_id

            cat_id_int = safe_int(cat_id)
            if cat_id_int is not None:
                category_id_to_yolo_id[cat_id_int] = yolo_id

            label_to_yolo_id[clean_label(cat_name)] = yolo_id

        return {
            "class_names": class_names,
            "allowed_labels": None,
            "label_to_yolo_id": label_to_yolo_id,
            "category_id_to_yolo_id": category_id_to_yolo_id,
        }

    raise ValueError(
        "Invalid yolo_class_mode. Use one of: "
        "person_related_single_class, person_related_multi_class, all_categories."
    )


def get_yolo_class_id(ann, id_to_name, yolo_config, yolo_class_mode):
    """
    Decide which YOLO class ID an annotation should get.

    Returns:
        int class id, or None if the annotation should be skipped.
    """
    label = clean_label(get_annotation_label(ann, id_to_name))
    category_id = ann.get("category_id")

    if yolo_class_mode == "person_related_single_class":
        if label in yolo_config["allowed_labels"]:
            return 0
        return None

    if yolo_class_mode == "person_related_multi_class":
        return yolo_config["label_to_yolo_id"].get(label)

    if yolo_class_mode == "all_categories":
        category_map = yolo_config["category_id_to_yolo_id"]

        if category_id in category_map:
            return category_map[category_id]

        category_id_str = str(category_id)
        if category_id_str in category_map:
            return category_map[category_id_str]

        category_id_int = safe_int(category_id)
        if category_id_int is not None and category_id_int in category_map:
            return category_map[category_id_int]

        return yolo_config["label_to_yolo_id"].get(label)

    return None


def coco_bbox_to_yolo(
    bbox,
    img_width,
    img_height,
    clip_boxes_to_image,
    min_box_width_pixels,
    min_box_height_pixels,
):
    """
    Convert COCO-style bbox to YOLO bbox.

    COCO-style format:
        [x_min, y_min, width, height]

    YOLO format:
        x_center_norm y_center_norm width_norm height_norm
    """
    if bbox is None or len(bbox) != 4:
        return None

    if img_width <= 0 or img_height <= 0:
        return None

    x, y, width, height = bbox

    x = float(x)
    y = float(y)
    width = float(width)
    height = float(height)

    if width <= 0 or height <= 0:
        return None

    x1 = x
    y1 = y
    x2 = x + width
    y2 = y + height

    if clip_boxes_to_image:
        x1 = max(0.0, min(x1, float(img_width)))
        y1 = max(0.0, min(y1, float(img_height)))
        x2 = max(0.0, min(x2, float(img_width)))
        y2 = max(0.0, min(y2, float(img_height)))

    clipped_width = x2 - x1
    clipped_height = y2 - y1

    if clipped_width < min_box_width_pixels:
        return None

    if clipped_height < min_box_height_pixels:
        return None

    x_center = x1 + clipped_width / 2.0
    y_center = y1 + clipped_height / 2.0

    x_center_norm = x_center / float(img_width)
    y_center_norm = y_center / float(img_height)
    width_norm = clipped_width / float(img_width)
    height_norm = clipped_height / float(img_height)

    x_center_norm = max(0.0, min(x_center_norm, 1.0))
    y_center_norm = max(0.0, min(y_center_norm, 1.0))
    width_norm = max(0.0, min(width_norm, 1.0))
    height_norm = max(0.0, min(height_norm, 1.0))

    if width_norm <= 0 or height_norm <= 0:
        return None

    return x_center_norm, y_center_norm, width_norm, height_norm


def image_file_to_label_file(image_file_name):
    """
    Convert:
        abc.jpg
    to:
        abc.txt
    """
    base_name = os.path.splitext(os.path.basename(image_file_name))[0]
    return base_name + ".txt"


def write_classes_file(yolo_classes_file, class_names):
    """Write classes.txt."""
    with yolo_classes_file.open("w", encoding="utf-8") as f:
        for name in class_names:
            f.write(str(name) + "\n")


def write_data_yaml(yolo_data_yaml_file, yolo_output_dir, class_names):
    """
    Write a simple Ultralytics-style data.yaml.

    Since this script creates one folder of images, train and val both point
    to images by default. Users can edit this later if they create separate
    train/val folders.
    """
    yolo_path = str(yolo_output_dir).replace("\\", "/")

    with yolo_data_yaml_file.open("w", encoding="utf-8") as f:
        f.write(f"path: {yolo_path}\n")
        f.write("train: images\n")
        f.write("val: images\n")
        f.write("\n")
        f.write("names:\n")

        for idx, name in enumerate(class_names):
            f.write(f"  {idx}: {name}\n")


# ============================================================
# MAIN SCRIPT
# ============================================================

def main():
    args = parse_args()
    paths = resolve_paths(args)
    validate_inputs(paths)

    filtered_images_dir = paths["filtered_images_dir"]
    filtered_annotations_file = paths["filtered_annotations_file"]
    yolo_output_dir = paths["yolo_output_dir"]
    yolo_images_dir = paths["yolo_images_dir"]
    yolo_labels_dir = paths["yolo_labels_dir"]
    yolo_classes_file = paths["yolo_classes_file"]
    yolo_data_yaml_file = paths["yolo_data_yaml_file"]
    yolo_summary_file = paths["yolo_summary_file"]

    print("Cityscapes--Pedestrian YOLO annotation creation")
    print("==============================================")
    print(f"Filtered images dir:      {filtered_images_dir}")
    print(f"Filtered annotations:     {filtered_annotations_file}")
    print(f"YOLO output dir:          {yolo_output_dir}")
    print(f"YOLO class mode:          {args.yolo_class_mode}")
    print(f"Clear YOLO output:        {args.clear_yolo_output_on_run}")
    print(f"Copy images:              {args.copy_images_to_yolo_folder}")
    print(f"Create empty labels:      {args.create_empty_label_files}")

    print("\nLoading filtered COCO-style annotations...")

    with filtered_annotations_file.open("r", encoding="utf-8") as f:
        coco_data = json.load(f)

    images = coco_data.get("images", [])
    annotations = coco_data.get("annotations", [])
    categories = coco_data.get("categories", [])

    print(f"Found {len(images)} images in JSON.")
    print(f"Found {len(annotations)} annotations in JSON.")
    print(f"Found {len(categories)} categories in JSON.")

    id_to_name = build_category_lookup(coco_data)

    yolo_config = build_yolo_class_mapping(
        coco_data=coco_data,
        yolo_class_mode=args.yolo_class_mode,
        single_person_class_name=args.single_person_class_name,
    )

    class_names = yolo_config["class_names"]

    print("")
    print("YOLO classes:")
    for idx, name in enumerate(class_names):
        print(f"  {idx}: {name}")

    # ============================================================
    # PREPARE OUTPUT FOLDERS
    # ============================================================

    if args.clear_yolo_output_on_run and yolo_output_dir.is_dir():
        print("")
        print(f"Clearing old YOLO output folder: {yolo_output_dir}")
        shutil.rmtree(yolo_output_dir)

    yolo_output_dir.mkdir(parents=True, exist_ok=True)
    yolo_labels_dir.mkdir(parents=True, exist_ok=True)

    if args.copy_images_to_yolo_folder:
        yolo_images_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # GROUP ANNOTATIONS BY IMAGE ID
    # ============================================================

    annotations_by_image_id = defaultdict(list)

    for ann in annotations:
        image_id = ann.get("image_id")
        annotations_by_image_id[image_id].append(ann)

    # ============================================================
    # CONVERT ANNOTATIONS
    # ============================================================

    print("")
    print("Converting COCO-style annotations to YOLO labels...")

    total_images_processed = 0
    total_images_copied = 0
    total_label_files_written = 0
    total_yolo_boxes_written = 0
    total_annotations_skipped_by_class = 0
    total_annotations_skipped_by_bbox = 0
    missing_image_files = 0

    for img in tqdm(images, desc="Creating YOLO labels"):
        image_id = img.get("id")
        image_file_name = img.get("file_name", "")

        img_width = img.get("width", 0)
        img_height = img.get("height", 0)

        if img_width is None:
            img_width = 0

        if img_height is None:
            img_height = 0

        img_width = int(img_width)
        img_height = int(img_height)

        if img_width <= 0 or img_height <= 0:
            print(
                f"Warning: image has invalid width/height, skipping: {image_file_name}"
            )
            continue

        source_image_path = filtered_images_dir / image_file_name

        if not source_image_path.exists():
            missing_image_files += 1
            print(f"Warning: missing image file, skipping: {source_image_path}")
            continue

        if args.copy_images_to_yolo_folder:
            destination_image_path = yolo_images_dir / image_file_name
            shutil.copy2(source_image_path, destination_image_path)
            total_images_copied += 1

        image_annotations = annotations_by_image_id.get(image_id, [])

        yolo_lines = []

        for ann in image_annotations:
            yolo_class_id = get_yolo_class_id(
                ann=ann,
                id_to_name=id_to_name,
                yolo_config=yolo_config,
                yolo_class_mode=args.yolo_class_mode,
            )

            if yolo_class_id is None:
                total_annotations_skipped_by_class += 1
                continue

            yolo_bbox = coco_bbox_to_yolo(
                bbox=ann.get("bbox"),
                img_width=img_width,
                img_height=img_height,
                clip_boxes_to_image=args.clip_boxes_to_image,
                min_box_width_pixels=args.min_box_width_pixels,
                min_box_height_pixels=args.min_box_height_pixels,
            )

            if yolo_bbox is None:
                total_annotations_skipped_by_bbox += 1
                continue

            x_center_norm, y_center_norm, width_norm, height_norm = yolo_bbox

            line = (
                f"{yolo_class_id} "
                f"{x_center_norm:.{args.yolo_decimals}f} "
                f"{y_center_norm:.{args.yolo_decimals}f} "
                f"{width_norm:.{args.yolo_decimals}f} "
                f"{height_norm:.{args.yolo_decimals}f}"
            )

            yolo_lines.append(line)

        label_file_name = image_file_to_label_file(image_file_name)
        label_file_path = yolo_labels_dir / label_file_name

        if yolo_lines or args.create_empty_label_files:
            with label_file_path.open("w", encoding="utf-8") as f:
                for line in yolo_lines:
                    f.write(line + "\n")

            total_label_files_written += 1
            total_yolo_boxes_written += len(yolo_lines)

        total_images_processed += 1

    # ============================================================
    # WRITE CLASSES AND DATA YAML
    # ============================================================

    write_classes_file(yolo_classes_file, class_names)
    write_data_yaml(yolo_data_yaml_file, yolo_output_dir, class_names)

    # ============================================================
    # WRITE SUMMARY
    # ============================================================

    summary = {
        "filtered_annotations_file": str(filtered_annotations_file),
        "filtered_images_dir": str(filtered_images_dir),
        "yolo_output_dir": str(yolo_output_dir),
        "yolo_images_dir": str(yolo_images_dir),
        "yolo_labels_dir": str(yolo_labels_dir),
        "yolo_class_mode": args.yolo_class_mode,
        "class_names": class_names,
        "images_in_json": len(images),
        "annotations_in_json": len(annotations),
        "categories_in_json": len(categories),
        "images_processed": total_images_processed,
        "images_copied": total_images_copied,
        "label_files_written": total_label_files_written,
        "yolo_boxes_written": total_yolo_boxes_written,
        "annotations_skipped_by_class": total_annotations_skipped_by_class,
        "annotations_skipped_by_bbox": total_annotations_skipped_by_bbox,
        "missing_image_files": missing_image_files,
    }

    with yolo_summary_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    # ============================================================
    # FINISHED
    # ============================================================

    print("")
    print("Done.")
    print(f"YOLO images folder: {yolo_images_dir}")
    print(f"YOLO labels folder: {yolo_labels_dir}")
    print(f"classes.txt: {yolo_classes_file}")
    print(f"data.yaml: {yolo_data_yaml_file}")
    print(f"summary: {yolo_summary_file}")

    print("")
    print("Summary:")
    print(f"Images in JSON: {len(images)}")
    print(f"Annotations in JSON: {len(annotations)}")
    print(f"Images processed: {total_images_processed}")
    print(f"Images copied: {total_images_copied}")
    print(f"Label files written: {total_label_files_written}")
    print(f"YOLO boxes written: {total_yolo_boxes_written}")
    print(f"Annotations skipped by class: {total_annotations_skipped_by_class}")
    print(f"Annotations skipped by bbox: {total_annotations_skipped_by_bbox}")
    print(f"Missing image files: {missing_image_files}")


if __name__ == "__main__":
    main()