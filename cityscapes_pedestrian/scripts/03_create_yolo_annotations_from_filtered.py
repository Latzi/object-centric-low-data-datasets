import os
import json
import shutil
from collections import defaultdict
from tqdm import tqdm


# ============================================================
# PATH SETUP
# ============================================================

PROCESSED_DIR = r"C:\Users\richm\Downloads\Cityscapes\processed"

# This is the folder created by your previous filtering script.
# It contains:
#   filtered_images/
#       image1.jpg
#       image2.jpg
#       filtered_annotations.json
FILTERED_DIR = os.path.join(PROCESSED_DIR, "filtered_images")

FILTERED_IMAGES_DIR = FILTERED_DIR
FILTERED_ANNOTATIONS_FILE = os.path.join(FILTERED_DIR, "filtered_annotations.json")

# YOLO output folder.
# The script will create:
#   processed/filtered_yolo/images/
#   processed/filtered_yolo/labels/
#   processed/filtered_yolo/classes.txt
#   processed/filtered_yolo/data.yaml
YOLO_OUTPUT_DIR = os.path.join(PROCESSED_DIR, "filtered_yolo")
YOLO_IMAGES_DIR = os.path.join(YOLO_OUTPUT_DIR, "images")
YOLO_LABELS_DIR = os.path.join(YOLO_OUTPUT_DIR, "labels")
YOLO_CLASSES_FILE = os.path.join(YOLO_OUTPUT_DIR, "classes.txt")
YOLO_DATA_YAML_FILE = os.path.join(YOLO_OUTPUT_DIR, "data.yaml")
YOLO_SUMMARY_FILE = os.path.join(YOLO_OUTPUT_DIR, "conversion_summary.json")

# Delete the old YOLO output folder before creating a new one.
CLEAR_YOLO_OUTPUT_ON_RUN = True

# Copy images into YOLO_OUTPUT_DIR/images.
# Recommended: True.
COPY_IMAGES_TO_YOLO_FOLDER = True

# Create an empty .txt label file for images that have no kept YOLO boxes.
# Recommended: True for YOLO datasets.
CREATE_EMPTY_LABEL_FILES = True


# ============================================================
# YOLO CLASS SETTINGS
# ============================================================

# Main mode.
#
# Options:
#
#   "person_related_single_class"
#       All person-related categories become YOLO class 0.
#       This matches your example where every line starts with 0.
#
#   "all_categories"
#       Every COCO category becomes a separate YOLO class.
#
#   "person_related_multi_class"
#       Person-related categories are kept as separate YOLO classes.
#
YOLO_CLASS_MODE = "person_related_single_class"


# These are the labels that will become YOLO class 0 when using:
#   YOLO_CLASS_MODE = "person_related_single_class"
#
# These match the person-like labels used in your earlier crop-generation scripts.
PERSON_RELATED_LABELS = [
    "pedestrian",
    "sitting person",
    "person group",
    "person (other)",
    "rider",
    "person",
    "persongroup",
    "ridergroup",
]

# Name of YOLO class 0 when using person_related_single_class.
SINGLE_PERSON_CLASS_NAME = "person"


# ============================================================
# BBOX SETTINGS
# ============================================================

# Clip boxes so they stay inside the image area.
# Recommended: True.
CLIP_BOXES_TO_IMAGE = True

# Ignore boxes that become too small after clipping.
MIN_BOX_WIDTH_PIXELS = 1.0
MIN_BOX_HEIGHT_PIXELS = 1.0

# Number of decimal places in YOLO labels.
YOLO_DECIMALS = 6


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

    # Fallback: maybe category_id is already a label.
    return category_id_str


def category_sort_key(cat):
    """Stable sorting key for COCO categories."""
    cat_id = cat.get("id")
    cat_id_int = safe_int(cat_id)

    if cat_id_int is not None:
        return (0, cat_id_int)

    return (1, str(cat_id))


def build_yolo_class_mapping(coco_data, id_to_name):
    """
    Build class names and label/category mappings for YOLO conversion.
    """
    categories = coco_data.get("categories", [])

    if YOLO_CLASS_MODE == "person_related_single_class":
        class_names = [SINGLE_PERSON_CLASS_NAME]

        allowed_labels = {clean_label(x) for x in PERSON_RELATED_LABELS}

        return {
            "class_names": class_names,
            "allowed_labels": allowed_labels,
            "label_to_yolo_id": None,
            "category_id_to_yolo_id": None,
        }

    elif YOLO_CLASS_MODE == "person_related_multi_class":
        class_names = list(PERSON_RELATED_LABELS)

        label_to_yolo_id = {}
        for idx, name in enumerate(class_names):
            label_to_yolo_id[clean_label(name)] = idx

        return {
            "class_names": class_names,
            "allowed_labels": set(label_to_yolo_id.keys()),
            "label_to_yolo_id": label_to_yolo_id,
            "category_id_to_yolo_id": None,
        }

    elif YOLO_CLASS_MODE == "all_categories":
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

    else:
        raise ValueError(
            "Invalid YOLO_CLASS_MODE. Use one of: "
            "'person_related_single_class', "
            "'person_related_multi_class', "
            "'all_categories'."
        )


def get_yolo_class_id(ann, id_to_name, yolo_config):
    """
    Decide which YOLO class ID an annotation should get.

    Returns:
        int class id, or None if the annotation should be skipped.
    """
    label = clean_label(get_annotation_label(ann, id_to_name))
    category_id = ann.get("category_id")

    if YOLO_CLASS_MODE == "person_related_single_class":
        if label in yolo_config["allowed_labels"]:
            return 0
        return None

    if YOLO_CLASS_MODE == "person_related_multi_class":
        return yolo_config["label_to_yolo_id"].get(label)

    if YOLO_CLASS_MODE == "all_categories":
        category_map = yolo_config["category_id_to_yolo_id"]

        if category_id in category_map:
            return category_map[category_id]

        category_id_str = str(category_id)
        if category_id_str in category_map:
            return category_map[category_id_str]

        category_id_int = safe_int(category_id)
        if category_id_int is not None and category_id_int in category_map:
            return category_map[category_id_int]

        # Fallback by label name.
        return yolo_config["label_to_yolo_id"].get(label)

    return None


def coco_bbox_to_yolo(bbox, img_width, img_height):
    """
    Convert COCO bbox to YOLO bbox.

    COCO format:
        [x_min, y_min, width, height]

    YOLO format:
        x_center_norm y_center_norm width_norm height_norm
    """
    if bbox is None or len(bbox) != 4:
        return None

    if img_width <= 0 or img_height <= 0:
        return None

    x, y, w, h = bbox

    x = float(x)
    y = float(y)
    w = float(w)
    h = float(h)

    if w <= 0 or h <= 0:
        return None

    x1 = x
    y1 = y
    x2 = x + w
    y2 = y + h

    if CLIP_BOXES_TO_IMAGE:
        x1 = max(0.0, min(x1, float(img_width)))
        y1 = max(0.0, min(y1, float(img_height)))
        x2 = max(0.0, min(x2, float(img_width)))
        y2 = max(0.0, min(y2, float(img_height)))

    clipped_w = x2 - x1
    clipped_h = y2 - y1

    if clipped_w < MIN_BOX_WIDTH_PIXELS:
        return None

    if clipped_h < MIN_BOX_HEIGHT_PIXELS:
        return None

    x_center = x1 + clipped_w / 2.0
    y_center = y1 + clipped_h / 2.0

    x_center_norm = x_center / float(img_width)
    y_center_norm = y_center / float(img_height)
    width_norm = clipped_w / float(img_width)
    height_norm = clipped_h / float(img_height)

    # Final safety clamp.
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


def write_classes_file(class_names):
    """Write classes.txt."""
    with open(YOLO_CLASSES_FILE, "w", encoding="utf-8") as f:
        for name in class_names:
            f.write(str(name) + "\n")


def write_data_yaml(class_names):
    """
    Write a simple Ultralytics-style data.yaml.

    Since this script creates one folder of images, train and val both point
    to images by default. You can edit this later if you create separate
    train/val folders.
    """
    yolo_path = YOLO_OUTPUT_DIR.replace("\\", "/")

    with open(YOLO_DATA_YAML_FILE, "w", encoding="utf-8") as f:
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

print("Loading filtered COCO annotations...")

with open(FILTERED_ANNOTATIONS_FILE, "r", encoding="utf-8") as f:
    coco_data = json.load(f)

images = coco_data.get("images", [])
annotations = coco_data.get("annotations", [])
categories = coco_data.get("categories", [])

print(f"Found {len(images)} images in JSON.")
print(f"Found {len(annotations)} annotations in JSON.")
print(f"Found {len(categories)} categories in JSON.")

id_to_name = build_category_lookup(coco_data)
yolo_config = build_yolo_class_mapping(coco_data, id_to_name)
class_names = yolo_config["class_names"]

print("")
print("YOLO class mode:", YOLO_CLASS_MODE)
print("YOLO classes:")
for idx, name in enumerate(class_names):
    print(f"  {idx}: {name}")


# ============================================================
# PREPARE OUTPUT FOLDERS
# ============================================================

if CLEAR_YOLO_OUTPUT_ON_RUN and os.path.isdir(YOLO_OUTPUT_DIR):
    print("")
    print(f"Clearing old YOLO output folder: {YOLO_OUTPUT_DIR}")
    shutil.rmtree(YOLO_OUTPUT_DIR)

os.makedirs(YOLO_OUTPUT_DIR, exist_ok=True)
os.makedirs(YOLO_LABELS_DIR, exist_ok=True)

if COPY_IMAGES_TO_YOLO_FOLDER:
    os.makedirs(YOLO_IMAGES_DIR, exist_ok=True)


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
print("Converting COCO annotations to YOLO labels...")

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
        print(f"Warning: image has invalid width/height, skipping: {image_file_name}")
        continue

    source_image_path = os.path.join(FILTERED_IMAGES_DIR, image_file_name)

    if not os.path.exists(source_image_path):
        missing_image_files += 1
        print(f"Warning: missing image file, skipping: {source_image_path}")
        continue

    if COPY_IMAGES_TO_YOLO_FOLDER:
        dest_image_path = os.path.join(YOLO_IMAGES_DIR, image_file_name)
        shutil.copy2(source_image_path, dest_image_path)
        total_images_copied += 1

    image_annotations = annotations_by_image_id.get(image_id, [])

    yolo_lines = []

    for ann in image_annotations:
        yolo_class_id = get_yolo_class_id(ann, id_to_name, yolo_config)

        if yolo_class_id is None:
            total_annotations_skipped_by_class += 1
            continue

        yolo_bbox = coco_bbox_to_yolo(
            bbox=ann.get("bbox"),
            img_width=img_width,
            img_height=img_height,
        )

        if yolo_bbox is None:
            total_annotations_skipped_by_bbox += 1
            continue

        x_center_norm, y_center_norm, width_norm, height_norm = yolo_bbox

        line = (
            f"{yolo_class_id} "
            f"{x_center_norm:.{YOLO_DECIMALS}f} "
            f"{y_center_norm:.{YOLO_DECIMALS}f} "
            f"{width_norm:.{YOLO_DECIMALS}f} "
            f"{height_norm:.{YOLO_DECIMALS}f}"
        )

        yolo_lines.append(line)

    label_file_name = image_file_to_label_file(image_file_name)
    label_file_path = os.path.join(YOLO_LABELS_DIR, label_file_name)

    if yolo_lines or CREATE_EMPTY_LABEL_FILES:
        with open(label_file_path, "w", encoding="utf-8") as f:
            for line in yolo_lines:
                f.write(line + "\n")

        total_label_files_written += 1
        total_yolo_boxes_written += len(yolo_lines)

    total_images_processed += 1


# ============================================================
# WRITE CLASSES AND DATA YAML
# ============================================================

write_classes_file(class_names)
write_data_yaml(class_names)


# ============================================================
# WRITE SUMMARY
# ============================================================

summary = {
    "filtered_annotations_file": FILTERED_ANNOTATIONS_FILE,
    "filtered_images_dir": FILTERED_IMAGES_DIR,
    "yolo_output_dir": YOLO_OUTPUT_DIR,
    "yolo_images_dir": YOLO_IMAGES_DIR,
    "yolo_labels_dir": YOLO_LABELS_DIR,
    "yolo_class_mode": YOLO_CLASS_MODE,
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

with open(YOLO_SUMMARY_FILE, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)


# ============================================================
# FINISHED
# ============================================================

print("")
print("Done.")
print(f"YOLO images folder: {YOLO_IMAGES_DIR}")
print(f"YOLO labels folder: {YOLO_LABELS_DIR}")
print(f"classes.txt: {YOLO_CLASSES_FILE}")
print(f"data.yaml: {YOLO_DATA_YAML_FILE}")
print(f"summary: {YOLO_SUMMARY_FILE}")

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