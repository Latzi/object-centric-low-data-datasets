import argparse
import csv
import json
import os
import random
import shutil
from collections import defaultdict

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_FILTERED_FOLDER_NAME = "filtered_images"
DEFAULT_CLEAR_FILTERED_FOLDER_ON_RUN = True

DEFAULT_MAX_SELECTED_IMAGES = 3000
DEFAULT_RANDOM_SEED = 42

# These are the person/pedestrian-related labels.
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
CUSTOM_COUNT_LABELS = {
    "person",
    "rider",
    "bicyclegroup",
    "motorcycle",
    "motorcyclegroup",
    "persongroup",
    "ridergroup",
}

DEFAULT_COUNT_LABEL_MODE = "person_related"
DEFAULT_COUNT_FILTER_MODE = "none"
DEFAULT_MIN_OBJECTS = 1
DEFAULT_MAX_OBJECTS = 5

DEFAULT_SELECTION_MODE = "most_overlap"

DEFAULT_MIN_PERSON_BOXES_FOR_OVERLAP = 2
DEFAULT_OVERLAP_IOU_THRESHOLD = 0.05
DEFAULT_OVERLAP_OVER_SMALLER_THRESHOLD = 0.50
DEFAULT_MIN_OVERLAPPING_PERSON_PAIRS = 1

DEFAULT_KEEP_ALL_CATEGORIES = True
DEFAULT_REINDEX_IDS = False


# ============================================================
# ARGUMENTS
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Filter locally generated Cityscapes--Pedestrian crops using object-count "
            "and person-overlap criteria."
        )
    )

    parser.add_argument(
        "--processed-dir",
        default=os.environ.get("CITYSCAPES_PROCESSED_DIR"),
        help=(
            "Path to the local processed Cityscapes--Pedestrian folder. "
            "Expected contents include cropped_images/ and cropped_annotations.json. "
            "You may also set CITYSCAPES_PROCESSED_DIR."
        ),
    )

    parser.add_argument(
        "--images-dir",
        default=None,
        help=(
            "Optional path to cropped_images. "
            "Default: PROCESSED_DIR/cropped_images."
        ),
    )

    parser.add_argument(
        "--annotations-file",
        default=None,
        help=(
            "Optional path to cropped_annotations.json. "
            "Default: PROCESSED_DIR/cropped_annotations.json."
        ),
    )

    parser.add_argument(
        "--filtered-folder-name",
        default=DEFAULT_FILTERED_FOLDER_NAME,
        help="Folder created inside processed-dir for filtered images. Default: filtered_images.",
    )

    parser.add_argument(
        "--filtered-dir",
        default=None,
        help=(
            "Optional output folder for filtered images and filtered annotations. "
            "Default: PROCESSED_DIR/FILTERED_FOLDER_NAME."
        ),
    )

    parser.add_argument(
        "--max-selected-images",
        type=int,
        default=DEFAULT_MAX_SELECTED_IMAGES,
        help=(
            "Maximum number of images to keep. Use -1 to keep all matching images. "
            "Default: 3000."
        ),
    )

    parser.add_argument(
        "--random-seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
        help="Random seed used only when --selection-mode random. Default: 42.",
    )

    parser.add_argument(
        "--count-label-mode",
        choices=["all", "person_related", "custom"],
        default=DEFAULT_COUNT_LABEL_MODE,
        help=(
            "Which annotation labels should be counted for object-count filtering. "
            "Default: person_related."
        ),
    )

    parser.add_argument(
        "--count-filter-mode",
        choices=["none", "min", "max", "range"],
        default=DEFAULT_COUNT_FILTER_MODE,
        help="How object-count filtering should be applied. Default: none.",
    )

    parser.add_argument(
        "--min-objects",
        type=int,
        default=DEFAULT_MIN_OBJECTS,
        help="Minimum object count used for min/range filtering. Default: 1.",
    )

    parser.add_argument(
        "--max-objects",
        type=int,
        default=DEFAULT_MAX_OBJECTS,
        help="Maximum object count used for max/range filtering. Default: 5.",
    )

    parser.add_argument(
        "--selection-mode",
        choices=[
            "lowest_count",
            "highest_count",
            "most_overlap",
            "least_overlap",
            "random",
        ],
        default=DEFAULT_SELECTION_MODE,
        help="How to rank/select images after filtering. Default: most_overlap.",
    )

    parser.add_argument(
        "--min-person-boxes-for-overlap",
        type=int,
        default=DEFAULT_MIN_PERSON_BOXES_FOR_OVERLAP,
        help="Minimum number of person-related boxes required for overlap selection. Default: 2.",
    )

    parser.add_argument(
        "--overlap-iou-threshold",
        type=float,
        default=DEFAULT_OVERLAP_IOU_THRESHOLD,
        help="IoU threshold for considering two person boxes overlapping. Default: 0.05.",
    )

    parser.add_argument(
        "--overlap-over-smaller-threshold",
        type=float,
        default=DEFAULT_OVERLAP_OVER_SMALLER_THRESHOLD,
        help=(
            "Intersection-over-smaller-box threshold for considering two person boxes "
            "overlapping. Default: 0.50."
        ),
    )

    parser.add_argument(
        "--min-overlapping-person-pairs",
        type=int,
        default=DEFAULT_MIN_OVERLAPPING_PERSON_PAIRS,
        help=(
            "Minimum number of overlapping person-related box pairs required for "
            "overlap-based selection. Default: 1."
        ),
    )

    parser.add_argument(
        "--keep-all-categories",
        dest="keep_all_categories",
        action="store_true",
        default=DEFAULT_KEEP_ALL_CATEGORIES,
        help="Keep all original categories in the filtered JSON. This is the default.",
    )

    parser.add_argument(
        "--only-used-categories",
        dest="keep_all_categories",
        action="store_false",
        help="Keep only categories used in the filtered annotations.",
    )

    parser.add_argument(
        "--reindex-ids",
        dest="reindex_ids",
        action="store_true",
        default=DEFAULT_REINDEX_IDS,
        help="Rewrite image and annotation IDs from 1..N.",
    )

    parser.add_argument(
        "--keep-original-ids",
        dest="reindex_ids",
        action="store_false",
        help="Keep original image and annotation IDs. This is the default.",
    )

    parser.add_argument(
        "--clear-filtered-folder",
        dest="clear_filtered_folder_on_run",
        action="store_true",
        default=DEFAULT_CLEAR_FILTERED_FOLDER_ON_RUN,
        help="Delete the old filtered folder before creating the new subset. This is the default.",
    )

    parser.add_argument(
        "--no-clear-filtered-folder",
        dest="clear_filtered_folder_on_run",
        action="store_false",
        help="Do not delete the old filtered folder before creating the new subset.",
    )

    return parser.parse_args()


# ============================================================
# PATH RESOLUTION AND VALIDATION
# ============================================================

def resolve_paths(args):
    if not args.processed_dir and not args.images_dir and not args.annotations_file:
        raise RuntimeError(
            "No input path was provided. Pass --processed-dir or provide both "
            "--images-dir and --annotations-file."
        )

    processed_dir = (
        os.path.abspath(args.processed_dir)
        if args.processed_dir
        else None
    )

    if args.images_dir:
        images_dir = os.path.abspath(args.images_dir)
    else:
        images_dir = os.path.join(processed_dir, "cropped_images")

    if args.annotations_file:
        annotations_file = os.path.abspath(args.annotations_file)
    else:
        annotations_file = os.path.join(processed_dir, "cropped_annotations.json")

    if args.filtered_dir:
        filtered_dir = os.path.abspath(args.filtered_dir)
    else:
        if processed_dir is None:
            raise RuntimeError(
                "No --filtered-dir was provided and --processed-dir is unavailable."
            )
        filtered_dir = os.path.join(processed_dir, args.filtered_folder_name)

    filtered_annotations_file = os.path.join(
        filtered_dir,
        "filtered_annotations.json",
    )
    filtered_stats_file = os.path.join(
        filtered_dir,
        "filtered_stats.csv",
    )

    return {
        "processed_dir": processed_dir,
        "images_dir": images_dir,
        "annotations_file": annotations_file,
        "filtered_dir": filtered_dir,
        "filtered_annotations_file": filtered_annotations_file,
        "filtered_stats_file": filtered_stats_file,
    }


def validate_inputs(paths):
    images_dir = paths["images_dir"]
    annotations_file = paths["annotations_file"]

    if not os.path.isdir(images_dir):
        raise FileNotFoundError(f"Images directory does not exist: {images_dir}")

    if not os.path.isfile(annotations_file):
        raise FileNotFoundError(
            f"Cropped annotations JSON does not exist: {annotations_file}"
        )


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

    return category_id_str


def get_count_label_set(count_label_mode):
    """Return which labels should be counted for object-count filtering."""
    if count_label_mode == "all":
        return None

    if count_label_mode == "person_related":
        return {clean_label(x) for x in PERSON_RELATED_LABELS}

    if count_label_mode == "custom":
        return {clean_label(x) for x in CUSTOM_COUNT_LABELS}

    raise ValueError(
        "Invalid count_label_mode. Use 'all', 'person_related', or 'custom'."
    )


def passes_object_count_filter(
    object_count,
    count_filter_mode,
    min_objects,
    max_objects,
):
    """Apply min/max/range object-count filter."""
    if count_filter_mode == "none":
        return True

    if count_filter_mode == "min":
        return object_count >= min_objects

    if count_filter_mode == "max":
        return object_count <= max_objects

    if count_filter_mode == "range":
        return min_objects <= object_count <= max_objects

    raise ValueError(
        "Invalid count_filter_mode. Use 'none', 'min', 'max', or 'range'."
    )


def bbox_area(bbox):
    """COCO bbox format: [x, y, width, height]."""
    if bbox is None or len(bbox) != 4:
        return 0.0

    _, _, width, height = bbox

    if width <= 0 or height <= 0:
        return 0.0

    return float(width) * float(height)


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

    inter_width = max(0.0, inter_right - inter_left)
    inter_height = max(0.0, inter_bottom - inter_top)

    return inter_width * inter_height


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


def compute_person_overlap_stats(
    person_annotations,
    overlap_iou_threshold,
    overlap_over_smaller_threshold,
):
    """
    Compute overlap statistics between all person-related boxes in one image.
    """
    total_pairs = 0
    overlapping_pair_count = 0

    overlap_score_sum = 0.0
    max_iou = 0.0
    max_overlap_over_smaller = 0.0

    number_of_annotations = len(person_annotations)

    for i in range(number_of_annotations):
        box_a = person_annotations[i].get("bbox", [0, 0, 0, 0])

        for j in range(i + 1, number_of_annotations):
            box_b = person_annotations[j].get("bbox", [0, 0, 0, 0])

            total_pairs += 1

            iou = bbox_iou(box_a, box_b)
            over_smaller = bbox_overlap_over_smaller(box_a, box_b)

            max_iou = max(max_iou, iou)
            max_overlap_over_smaller = max(max_overlap_over_smaller, over_smaller)

            is_overlapping_pair = (
                iou >= overlap_iou_threshold
                or over_smaller >= overlap_over_smaller_threshold
            )

            if is_overlapping_pair:
                overlapping_pair_count += 1
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


def sort_image_stats(image_stats, selection_mode, random_seed):
    """Sort candidate images according to selection mode."""
    if selection_mode == "lowest_count":
        return sorted(
            image_stats,
            key=lambda x: (
                x["counted_object_count"],
                x["person_related_count"],
                x["total_annotation_count"],
                x["image_id"],
            ),
        )

    if selection_mode == "highest_count":
        return sorted(
            image_stats,
            key=lambda x: (
                -x["counted_object_count"],
                -x["person_related_count"],
                -x["total_annotation_count"],
                x["image_id"],
            ),
        )

    if selection_mode == "most_overlap":
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

    if selection_mode == "least_overlap":
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

    if selection_mode == "random":
        output = list(image_stats)
        random.Random(random_seed).shuffle(output)
        return output

    raise ValueError(
        "Invalid selection_mode. Use 'lowest_count', 'highest_count', "
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


def build_filtered_categories(coco_data, filtered_annotations, keep_all_categories):
    """Return category list for the filtered JSON."""
    if keep_all_categories:
        return coco_data.get("categories", [])

    used_category_ids = {ann.get("category_id") for ann in filtered_annotations}

    return [
        cat for cat in coco_data.get("categories", [])
        if cat.get("id") in used_category_ids
    ]


def maybe_reindex_coco(
    filtered_images,
    filtered_annotations,
    filtered_categories,
    coco_data,
    reindex_ids,
):
    """Optionally reindex image and annotation IDs."""
    if not reindex_ids:
        return {
            "info": coco_data.get("info", {}),
            "licenses": coco_data.get("licenses", []),
            "images": filtered_images,
            "annotations": filtered_annotations,
            "categories": filtered_categories,
        }

    old_to_new_image_id = {}
    new_images = []

    for new_image_id, image in enumerate(filtered_images, start=1):
        old_image_id = image["id"]
        old_to_new_image_id[old_image_id] = new_image_id

        new_image = dict(image)
        new_image["id"] = new_image_id
        new_images.append(new_image)

    new_annotations = []

    for new_annotation_id, annotation in enumerate(filtered_annotations, start=1):
        old_image_id = annotation["image_id"]

        if old_image_id not in old_to_new_image_id:
            continue

        new_annotation = dict(annotation)
        new_annotation["id"] = new_annotation_id
        new_annotation["image_id"] = old_to_new_image_id[old_image_id]
        new_annotations.append(new_annotation)

    return {
        "info": coco_data.get("info", {}),
        "licenses": coco_data.get("licenses", []),
        "images": new_images,
        "annotations": new_annotations,
        "categories": filtered_categories,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    args = parse_args()
    paths = resolve_paths(args)
    validate_inputs(paths)

    images_dir = paths["images_dir"]
    annotations_file = paths["annotations_file"]
    filtered_dir = paths["filtered_dir"]
    filtered_annotations_file = paths["filtered_annotations_file"]
    filtered_stats_file = paths["filtered_stats_file"]

    max_selected_images = args.max_selected_images
    if max_selected_images is not None and max_selected_images < 0:
        max_selected_images = None

    print("Cityscapes--Pedestrian crop filtering")
    print("=====================================")
    print(f"Processed dir:           {paths['processed_dir']}")
    print(f"Images dir:              {images_dir}")
    print(f"Annotations file:        {annotations_file}")
    print(f"Filtered dir:            {filtered_dir}")
    print(f"Filtered annotations:    {filtered_annotations_file}")
    print(f"Filtered stats CSV:      {filtered_stats_file}")
    print(f"Max selected images:     {max_selected_images}")
    print(f"Count label mode:        {args.count_label_mode}")
    print(f"Count filter mode:       {args.count_filter_mode}")
    print(f"Selection mode:          {args.selection_mode}")
    print(f"Clear filtered folder:   {args.clear_filtered_folder_on_run}")

    print("\nLoading annotations...")

    with open(annotations_file, "r", encoding="utf-8") as f:
        coco_data = json.load(f)

    images = coco_data.get("images", [])
    annotations = coco_data.get("annotations", [])
    categories = coco_data.get("categories", [])

    print(f"Found {len(images)} images.")
    print(f"Found {len(annotations)} annotations.")
    print(f"Found {len(categories)} categories.")

    id_to_name = build_category_lookup(coco_data)

    count_label_set = get_count_label_set(args.count_label_mode)
    overlap_label_set = {clean_label(x) for x in PERSON_RELATED_LABELS}

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

            if count_label_set is None:
                counted_object_count += 1
            elif label in count_label_set:
                counted_object_count += 1

            if label in overlap_label_set:
                person_related_annotations.append(ann)

        overlap_stats = compute_person_overlap_stats(
            person_annotations=person_related_annotations,
            overlap_iou_threshold=args.overlap_iou_threshold,
            overlap_over_smaller_threshold=args.overlap_over_smaller_threshold,
        )

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

    overlap_selection = args.selection_mode in {"most_overlap", "least_overlap"}

    for row in all_image_stats:
        if not passes_object_count_filter(
            object_count=row["counted_object_count"],
            count_filter_mode=args.count_filter_mode,
            min_objects=args.min_objects,
            max_objects=args.max_objects,
        ):
            continue

        if overlap_selection:
            if row["person_related_count"] < args.min_person_boxes_for_overlap:
                continue

            if row["overlapping_person_pair_count"] < args.min_overlapping_person_pairs:
                continue

        candidate_stats.append(row)

    print(f"Candidate images after filtering: {len(candidate_stats)}")

    # ============================================================
    # SORT AND SELECT FINAL IMAGES
    # ============================================================

    sorted_stats = sort_image_stats(
        image_stats=candidate_stats,
        selection_mode=args.selection_mode,
        random_seed=args.random_seed,
    )

    if max_selected_images is None:
        selected_stats = sorted_stats
    else:
        selected_stats = sorted_stats[:max_selected_images]

    selected_image_ids = {row["image_id"] for row in selected_stats}

    print(f"Selected images before copy check: {len(selected_image_ids)}")

    # ============================================================
    # CREATE OUTPUT FOLDER
    # ============================================================

    if args.clear_filtered_folder_on_run and os.path.isdir(filtered_dir):
        print(f"\nClearing old filtered folder: {filtered_dir}")
        shutil.rmtree(filtered_dir)

    os.makedirs(filtered_dir, exist_ok=True)

    # ============================================================
    # COPY SELECTED IMAGES
    # ============================================================

    print("\nCopying selected images...")

    filtered_images = []
    copied_image_ids = set()
    copied_stats = []

    missing_count = 0

    for row in tqdm(selected_stats, desc="Copying images"):
        image_id = row["image_id"]
        image = images_by_id.get(image_id)

        if image is None:
            continue

        file_name = image.get("file_name", "")

        source_path = os.path.join(images_dir, file_name)
        destination_path = os.path.join(filtered_dir, file_name)

        if not os.path.exists(source_path):
            missing_count += 1
            continue

        shutil.copy2(source_path, destination_path)

        filtered_images.append(image)
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

    filtered_categories = build_filtered_categories(
        coco_data=coco_data,
        filtered_annotations=filtered_annotations,
        keep_all_categories=args.keep_all_categories,
    )

    filtered_coco = maybe_reindex_coco(
        filtered_images=filtered_images,
        filtered_annotations=filtered_annotations,
        filtered_categories=filtered_categories,
        coco_data=coco_data,
        reindex_ids=args.reindex_ids,
    )

    # ============================================================
    # SAVE OUTPUTS
    # ============================================================

    with open(filtered_annotations_file, "w", encoding="utf-8") as f:
        json.dump(filtered_coco, f, indent=4)

    write_stats_csv(filtered_stats_file, copied_stats)

    print("\nDone.")
    print(f"Filtered images folder: {filtered_dir}")
    print(f"Filtered annotations: {filtered_annotations_file}")
    print(f"Stats CSV: {filtered_stats_file}")
    print(f"Images copied: {len(filtered_images)}")
    print(f"Annotations kept: {len(filtered_annotations)}")


if __name__ == "__main__":
    main()


# ============================================================
# CONFIG EXAMPLES
# ============================================================
#
# Example 1:
# Select images with the most overlapping pedestrian/person boxes:
#
#   --count-label-mode person_related
#   --count-filter-mode none
#   --selection-mode most_overlap
#   --min-overlapping-person-pairs 1
#
#
# Example 2:
# Select images with at least 4 person-related objects:
#
#   --count-label-mode person_related
#   --count-filter-mode min
#   --min-objects 4
#   --selection-mode highest_count
#
#
# Example 3:
# Select images with at most 2 person-related objects:
#
#   --count-label-mode person_related
#   --count-filter-mode max
#   --max-objects 2
#   --selection-mode lowest_count
#
#
# Example 4:
# Select images with between 2 and 6 person-related objects:
#
#   --count-label-mode person_related
#   --count-filter-mode range
#   --min-objects 2
#   --max-objects 6
#   --selection-mode highest_count
#
#
# Example 5:
# Select images with the most total annotations, not just person annotations:
#
#   --count-label-mode all
#   --count-filter-mode none
#   --selection-mode highest_count