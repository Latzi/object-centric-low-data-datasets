import os
import json
import shutil
import random
import csv
from collections import defaultdict
from tqdm import tqdm


# ============================================================
# PATH SETUP
# ============================================================

PROCESSED_DIR = r"C:\Users\richm\Downloads\Cityscapes\processed"

IMAGES_DIR = os.path.join(PROCESSED_DIR, "cropped_images")
ANNOTATIONS_FILE = os.path.join(PROCESSED_DIR, "cropped_annotations.json")

# This folder will be created inside PROCESSED_DIR.
# Images will be copied directly into this folder.
FILTERED_FOLDER_NAME = "filtered_images"

FILTERED_DIR = os.path.join(PROCESSED_DIR, FILTERED_FOLDER_NAME)
FILTERED_ANNOTATIONS_FILE = os.path.join(FILTERED_DIR, "filtered_annotations.json")
FILTERED_STATS_FILE = os.path.join(FILTERED_DIR, "filtered_stats.csv")

# If True, delete the old filtered folder before creating the new subset.
CLEAR_FILTERED_FOLDER_ON_RUN = True


# ============================================================
# MAIN SUBSET SETTINGS
# ============================================================

# Maximum number of images to keep in the final subset.
# Use None if you want to keep all matching images.
MAX_SELECTED_IMAGES = 3000

# Random seed used only if SELECTION_MODE = "random".
RANDOM_SEED = 42


# ============================================================
# CATEGORY GROUPS
# ============================================================

# These are the person/pedestrian-related labels.
#
# This is important because your earlier crop-generation script treats
# pedestrians as a broader group of labels, not just one single class.
#
# These labels may come from CityPersons and/or gtCoarse.
PERSON_RELATED_LABELS = {
    "pedestrian",
    "sitting person",
    "person group",
    "person (other)",
    "rider",
    "person",
    "persongroup",
    "ridergroup",
}

# Optional custom label set.
# Use this if you want to count a different group of labels.
CUSTOM_COUNT_LABELS = {
    "person",
    "rider",
    "bicyclegroup",
    "motorcycle",
    "motorcyclegroup",
    "persongroup",
    "ridergroup",
}


# ============================================================
# OBJECT COUNT FILTER SETTINGS
# ============================================================

# What objects should be counted?
#
# Options:
#   "all"             -> count all annotations in each image
#   "person_related"  -> count only PERSON_RELATED_LABELS
#   "custom"          -> count only CUSTOM_COUNT_LABELS
COUNT_LABEL_MODE = "person_related"

# How should the object count filter work?
#
# Options:
#   "none"   -> no min/max object-count filtering
#   "min"    -> keep images with object_count >= MIN_OBJECTS
#   "max"    -> keep images with object_count <= MAX_OBJECTS
#   "range"  -> keep images with MIN_OBJECTS <= object_count <= MAX_OBJECTS
COUNT_FILTER_MODE = "none"

# Used when COUNT_FILTER_MODE = "min" or "range".
MIN_OBJECTS = 1

# Used when COUNT_FILTER_MODE = "max" or "range".
MAX_OBJECTS = 5


# ============================================================
# SELECTION / SORTING MODE
# ============================================================

# After filtering, how should images be selected?
#
# Options:
#   "lowest_count"         -> select images with the fewest counted objects
#   "highest_count"        -> select images with the most counted objects
#   "most_overlap"         -> select images with the most overlapping person-related boxes
#   "least_overlap"        -> select images with the least overlapping person-related boxes
#   "random"               -> random selection after filtering
#
# For your specific question:
#   Use "most_overlap" to select images with the most overlapping pedestrian/person boxes.
SELECTION_MODE = "most_overlap"


# ============================================================
# PERSON-OVERLAP SETTINGS
# ============================================================

# For overlap scoring, we look only at person-related labels.
OVERLAP_LABELS = PERSON_RELATED_LABELS

# An image must have at least this many person-related annotations
# to be considered for overlap-based selection.
MIN_PERSON_BOXES_FOR_OVERLAP = 2

# A pair of person boxes is considered overlapping if:
#
#   IoU >= OVERLAP_IOU_THRESHOLD
#
# OR:
#
#   intersection_area / smaller_box_area >= OVERLAP_OVER_SMALLER_THRESHOLD
#
# The second condition is useful because one box may be much larger
# than another, for example:
#
#   CityPersons pedestrian box
#   gtCoarse person polygon converted to bbox
#
# In that case, the smaller box may be mostly inside the larger box,
# even if normal IoU is not very high.
OVERLAP_IOU_THRESHOLD = 0.05
OVERLAP_OVER_SMALLER_THRESHOLD = 0.50

# If using SELECTION_MODE = "most_overlap", this controls whether
# images with zero overlapping person pairs are allowed.
#
# Use 1 if you only want images that actually contain overlapping
# person-related boxes.
#
# Use 0 if you want all images ranked by overlap, even if some have no overlap.
MIN_OVERLAPPING_PERSON_PAIRS = 1


# ============================================================
# OUTPUT JSON SETTINGS
# ============================================================

# Keep all original categories in the filtered JSON.
# Usually this is safest for COCO-style training.
KEEP_ALL_CATEGORIES = True

# If True, rewrite image IDs and annotation IDs from 1..N.
# If False, keep the original IDs from cropped_annotations.json.
REINDEX_IDS = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_label(label):
    """Normalize category labels for comparison."""
    return str(label).strip().lower()


def build_category_lookup(coco_data):
    """
    Build a lookup so we can convert category_id to category name.

    COCO annotations normally store:
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

        try:
            id_to_name[int(cat_id)] = cat_name
        except Exception:
            pass

    return id_to_name


def get_annotation_label(ann, id_to_name):
    """
    Return the readable category label for an annotation.

    Handles normal COCO category IDs, and also handles the case where
    category_id is already a string label.
    """
    category_id = ann.get("category_id")

    if category_id in id_to_name:
        return id_to_name[category_id]

    category_id_str = str(category_id)
    if category_id_str in id_to_name:
        return id_to_name[category_id_str]

    try:
        category_id_int = int(category_id)
        if category_id_int in id_to_name:
            return id_to_name[category_id_int]
    except Exception:
        pass

    # Fallback: maybe category_id is already a label like "person".
    return category_id_str


def get_count_label_set():
    """Return which labels should be counted for object-count filtering."""
    if COUNT_LABEL_MODE == "all":
        return None

    if COUNT_LABEL_MODE == "person_related":
        return {clean_label(x) for x in PERSON_RELATED_LABELS}

    if COUNT_LABEL_MODE == "custom":
        return {clean_label(x) for x in CUSTOM_COUNT_LABELS}

    raise ValueError(
        "Invalid COUNT_LABEL_MODE. Use 'all', 'person_related', or 'custom'."
    )


def passes_object_count_filter(object_count):
    """Apply min/max/range object count filter."""
    if COUNT_FILTER_MODE == "none":
        return True

    if COUNT_FILTER_MODE == "min":
        return object_count >= MIN_OBJECTS

    if COUNT_FILTER_MODE == "max":
        return object_count <= MAX_OBJECTS

    if COUNT_FILTER_MODE == "range":
        return MIN_OBJECTS <= object_count <= MAX_OBJECTS

    raise ValueError(
        "Invalid COUNT_FILTER_MODE. Use 'none', 'min', 'max', or 'range'."
    )


def bbox_area(bbox):
    """COCO bbox format: [x, y, width, height]."""
    if bbox is None or len(bbox) != 4:
        return 0.0

    _, _, w, h = bbox

    if w <= 0 or h <= 0:
        return 0.0

    return float(w) * float(h)


def bbox_intersection_area(box_a, box_b):
    """Calculate intersection area between two COCO-format bounding boxes."""
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b

    a_left = float(ax)
    a_top = float(ay)
    a_right = float(ax) + float(aw)
    a_bottom = float(ay) + float(ah)

    b_left = float(bx)
    b_top = float(by)
    b_right = float(bx) + float(bw)
    b_bottom = float(by) + float(bh)

    inter_left = max(a_left, b_left)
    inter_top = max(a_top, b_top)
    inter_right = min(a_right, b_right)
    inter_bottom = min(a_bottom, b_bottom)

    inter_w = max(0.0, inter_right - inter_left)
    inter_h = max(0.0, inter_bottom - inter_top)

    return inter_w * inter_h


def bbox_iou(box_a, box_b):
    """Calculate IoU between two COCO-format bounding boxes."""
    area_a = bbox_area(box_a)
    area_b = bbox_area(box_b)

    if area_a <= 0 or area_b <= 0:
        return 0.0

    inter_area = bbox_intersection_area(box_a, box_b)
    union_area = area_a + area_b - inter_area

    if union_area <= 0:
        return 0.0

    return inter_area / union_area


def bbox_overlap_over_smaller(box_a, box_b):
    """
    Calculate intersection_area / smaller_box_area.

    This is useful when one box is much larger than the other.
    For duplicate or overlapping person boxes, this can be more useful than IoU.
    """
    area_a = bbox_area(box_a)
    area_b = bbox_area(box_b)

    if area_a <= 0 or area_b <= 0:
        return 0.0

    inter_area = bbox_intersection_area(box_a, box_b)
    smaller_area = min(area_a, area_b)

    if smaller_area <= 0:
        return 0.0

    return inter_area / smaller_area


def compute_person_overlap_stats(person_annotations):
    """
    Compute overlap statistics between all person-related boxes in one image.

    This is what lets us select images with the most overlapping pedestrian /
    person / rider / person-group boxes.
    """
    total_pairs = 0
    overlapping_pair_count = 0

    overlap_score_sum = 0.0
    max_iou = 0.0
    max_overlap_over_smaller = 0.0

    n = len(person_annotations)

    for i in range(n):
        box_a = person_annotations[i].get("bbox", [0, 0, 0, 0])

        for j in range(i + 1, n):
            box_b = person_annotations[j].get("bbox", [0, 0, 0, 0])

            total_pairs += 1

            iou = bbox_iou(box_a, box_b)
            over_smaller = bbox_overlap_over_smaller(box_a, box_b)

            max_iou = max(max_iou, iou)
            max_overlap_over_smaller = max(max_overlap_over_smaller, over_smaller)

            is_overlapping_pair = (
                iou >= OVERLAP_IOU_THRESHOLD or
                over_smaller >= OVERLAP_OVER_SMALLER_THRESHOLD
            )

            if is_overlapping_pair:
                overlapping_pair_count += 1

                # Use the stronger overlap measure as the score contribution.
                overlap_score_sum += max(iou, over_smaller)

    if overlapping_pair_count > 0:
        mean_overlap_score = overlap_score_sum / overlapping_pair_count
    else:
        mean_overlap_score = 0.0

    return {
        "person_pair_count": total_pairs,
        "overlapping_person_pair_count": overlapping_pair_count,
        "overlap_score_sum": overlap_score_sum,
        "mean_overlap_score": mean_overlap_score,
        "max_iou": max_iou,
        "max_overlap_over_smaller": max_overlap_over_smaller,
    }


def sort_image_stats(image_stats):
    """Sort candidate images according to SELECTION_MODE."""
    if SELECTION_MODE == "lowest_count":
        return sorted(
            image_stats,
            key=lambda x: (
                x["counted_object_count"],
                x["person_related_count"],
                x["total_annotation_count"],
                x["image_id"],
            ),
        )

    if SELECTION_MODE == "highest_count":
        return sorted(
            image_stats,
            key=lambda x: (
                -x["counted_object_count"],
                -x["person_related_count"],
                -x["total_annotation_count"],
                x["image_id"],
            ),
        )

    if SELECTION_MODE == "most_overlap":
        return sorted(
            image_stats,
            key=lambda x: (
                -x["overlapping_person_pair_count"],
                -x["overlap_score_sum"],
                -x["max_overlap_over_smaller"],
                -x["max_iou"],
                -x["person_related_count"],
                -x["counted_object_count"],
                x["image_id"],
            ),
        )

    if SELECTION_MODE == "least_overlap":
        return sorted(
            image_stats,
            key=lambda x: (
                x["overlapping_person_pair_count"],
                x["overlap_score_sum"],
                x["max_overlap_over_smaller"],
                x["max_iou"],
                x["person_related_count"],
                x["counted_object_count"],
                x["image_id"],
            ),
        )

    if SELECTION_MODE == "random":
        output = list(image_stats)
        random.Random(RANDOM_SEED).shuffle(output)
        return output

    raise ValueError(
        "Invalid SELECTION_MODE. Use 'lowest_count', 'highest_count', "
        "'most_overlap', 'least_overlap', or 'random'."
    )


def write_stats_csv(stats_file, selected_stats):
    """Write a CSV report showing why each image was selected."""
    fieldnames = [
        "image_id",
        "file_name",
        "total_annotation_count",
        "counted_object_count",
        "person_related_count",
        "person_pair_count",
        "overlapping_person_pair_count",
        "overlap_score_sum",
        "mean_overlap_score",
        "max_iou",
        "max_overlap_over_smaller",
    ]

    with open(stats_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in selected_stats:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def build_filtered_categories(coco_data, filtered_annotations):
    """Return category list for the filtered JSON."""
    if KEEP_ALL_CATEGORIES:
        return coco_data.get("categories", [])

    used_category_ids = {ann.get("category_id") for ann in filtered_annotations}

    return [
        cat for cat in coco_data.get("categories", [])
        if cat.get("id") in used_category_ids
    ]


def maybe_reindex_coco(filtered_images, filtered_annotations, filtered_categories, coco_data):
    """Optionally reindex image and annotation IDs."""
    if not REINDEX_IDS:
        return {
            "info": coco_data.get("info", {}),
            "licenses": coco_data.get("licenses", []),
            "images": filtered_images,
            "annotations": filtered_annotations,
            "categories": filtered_categories,
        }

    old_to_new_image_id = {}
    new_images = []

    for new_image_id, img in enumerate(filtered_images, start=1):
        old_image_id = img["id"]
        old_to_new_image_id[old_image_id] = new_image_id

        new_img = dict(img)
        new_img["id"] = new_image_id
        new_images.append(new_img)

    new_annotations = []

    for new_ann_id, ann in enumerate(filtered_annotations, start=1):
        old_image_id = ann["image_id"]

        if old_image_id not in old_to_new_image_id:
            continue

        new_ann = dict(ann)
        new_ann["id"] = new_ann_id
        new_ann["image_id"] = old_to_new_image_id[old_image_id]
        new_annotations.append(new_ann)

    return {
        "info": coco_data.get("info", {}),
        "licenses": coco_data.get("licenses", []),
        "images": new_images,
        "annotations": new_annotations,
        "categories": filtered_categories,
    }


# ============================================================
# MAIN SCRIPT
# ============================================================

print("Loading annotations...")

with open(ANNOTATIONS_FILE, "r", encoding="utf-8") as f:
    coco_data = json.load(f)

images = coco_data.get("images", [])
annotations = coco_data.get("annotations", [])
categories = coco_data.get("categories", [])

print(f"Found {len(images)} images.")
print(f"Found {len(annotations)} annotations.")
print(f"Found {len(categories)} categories.")

id_to_name = build_category_lookup(coco_data)

count_label_set = get_count_label_set()
overlap_label_set = {clean_label(x) for x in OVERLAP_LABELS}

images_by_id = {img["id"]: img for img in images}

annotations_by_image_id = defaultdict(list)
for ann in annotations:
    annotations_by_image_id[ann["image_id"]].append(ann)


# ============================================================
# CALCULATE PER-IMAGE STATS
# ============================================================

print("\nCalculating per-image object counts and overlap scores...")

all_image_stats = []

for img in tqdm(images, desc="Analyzing images"):
    image_id = img["id"]
    file_name = img.get("file_name", "")

    image_annotations = annotations_by_image_id.get(image_id, [])

    total_annotation_count = len(image_annotations)
    counted_object_count = 0
    person_related_annotations = []

    for ann in image_annotations:
        label = clean_label(get_annotation_label(ann, id_to_name))

        # Count object depending on COUNT_LABEL_MODE.
        if count_label_set is None:
            counted_object_count += 1
        elif label in count_label_set:
            counted_object_count += 1

        # Collect boxes for overlap scoring.
        if label in overlap_label_set:
            person_related_annotations.append(ann)

    overlap_stats = compute_person_overlap_stats(person_related_annotations)

    row = {
        "image_id": image_id,
        "file_name": file_name,
        "total_annotation_count": total_annotation_count,
        "counted_object_count": counted_object_count,
        "person_related_count": len(person_related_annotations),
    }

    row.update(overlap_stats)

    all_image_stats.append(row)


# ============================================================
# APPLY FILTERS
# ============================================================

print("\nApplying filters...")

candidate_stats = []

overlap_selection = SELECTION_MODE in {"most_overlap", "least_overlap"}

for row in all_image_stats:
    # Min/max/range object count filter.
    if not passes_object_count_filter(row["counted_object_count"]):
        continue

    # Extra requirements for overlap-based selection.
    if overlap_selection:
        if row["person_related_count"] < MIN_PERSON_BOXES_FOR_OVERLAP:
            continue

        if row["overlapping_person_pair_count"] < MIN_OVERLAPPING_PERSON_PAIRS:
            continue

    candidate_stats.append(row)

print(f"Candidate images after filtering: {len(candidate_stats)}")


# ============================================================
# SORT AND SELECT FINAL IMAGES
# ============================================================

sorted_stats = sort_image_stats(candidate_stats)

if MAX_SELECTED_IMAGES is None:
    selected_stats = sorted_stats
else:
    selected_stats = sorted_stats[:MAX_SELECTED_IMAGES]

selected_image_ids = {row["image_id"] for row in selected_stats}

print(f"Selected images before copy check: {len(selected_image_ids)}")


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

if CLEAR_FILTERED_FOLDER_ON_RUN and os.path.isdir(FILTERED_DIR):
    print(f"\nClearing old filtered folder: {FILTERED_DIR}")
    shutil.rmtree(FILTERED_DIR)

os.makedirs(FILTERED_DIR, exist_ok=True)


# ============================================================
# COPY SELECTED IMAGES
# ============================================================

print("\nCopying selected images...")

filtered_images = []
copied_image_ids = set()
copied_stats = []

selected_stats_by_image_id = {row["image_id"]: row for row in selected_stats}

missing_count = 0

# Copy in selected sorted order, not random set order.
for row in tqdm(selected_stats, desc="Copying images"):
    image_id = row["image_id"]
    img = images_by_id.get(image_id)

    if img is None:
        continue

    file_name = img.get("file_name", "")

    source_path = os.path.join(IMAGES_DIR, file_name)
    dest_path = os.path.join(FILTERED_DIR, file_name)

    if not os.path.exists(source_path):
        missing_count += 1
        continue

    shutil.copy2(source_path, dest_path)

    filtered_images.append(img)
    copied_image_ids.add(image_id)
    copied_stats.append(row)


print(f"Copied {len(filtered_images)} images.")
print(f"Missing source images: {missing_count}")


# ============================================================
# CREATE FILTERED ANNOTATIONS
# ============================================================

filtered_annotations = [
    ann for ann in annotations
    if ann["image_id"] in copied_image_ids
]

filtered_categories = build_filtered_categories(coco_data, filtered_annotations)

filtered_coco = maybe_reindex_coco(
    filtered_images=filtered_images,
    filtered_annotations=filtered_annotations,
    filtered_categories=filtered_categories,
    coco_data=coco_data,
)


# ============================================================
# SAVE OUTPUTS
# ============================================================

with open(FILTERED_ANNOTATIONS_FILE, "w", encoding="utf-8") as f:
    json.dump(filtered_coco, f, indent=4)

write_stats_csv(FILTERED_STATS_FILE, copied_stats)

print("\nDone.")
print(f"Filtered images folder: {FILTERED_DIR}")
print(f"Filtered annotations: {FILTERED_ANNOTATIONS_FILE}")
print(f"Stats CSV: {FILTERED_STATS_FILE}")
print(f"Images copied: {len(filtered_images)}")
print(f"Annotations kept: {len(filtered_annotations)}")


# ============================================================
# CONFIG EXAMPLES
# ============================================================
#
# Example 1:
# Select images with the most overlapping pedestrian/person boxes:
#
#   COUNT_LABEL_MODE = "person_related"
#   COUNT_FILTER_MODE = "none"
#   SELECTION_MODE = "most_overlap"
#   MIN_OVERLAPPING_PERSON_PAIRS = 1
#
#
# Example 2:
# Select images with at least 4 person-related objects:
#
#   COUNT_LABEL_MODE = "person_related"
#   COUNT_FILTER_MODE = "min"
#   MIN_OBJECTS = 4
#   SELECTION_MODE = "highest_count"
#
#
# Example 3:
# Select images with at most 2 person-related objects:
#
#   COUNT_LABEL_MODE = "person_related"
#   COUNT_FILTER_MODE = "max"
#   MAX_OBJECTS = 2
#   SELECTION_MODE = "lowest_count"
#
#
# Example 4:
# Select images with between 2 and 6 person-related objects:
#
#   COUNT_LABEL_MODE = "person_related"
#   COUNT_FILTER_MODE = "range"
#   MIN_OBJECTS = 2
#   MAX_OBJECTS = 6
#   SELECTION_MODE = "highest_count"
#
#
# Example 5:
# Select images with the most total annotations, not just person annotations:
#
#   COUNT_LABEL_MODE = "all"
#   COUNT_FILTER_MODE = "none"
#   SELECTION_MODE = "highest_count"