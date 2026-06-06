import argparse
import json
import os
import random
import shutil

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


cv2 = None


# ================================
# DEFAULT SETTINGS
# ================================

DEFAULT_SPLITS = ["train", "val"]

DEFAULT_DRAW_BB_DEBUG = True
DEFAULT_CLEAR_BB_DIR_ON_RUN = True
DEFAULT_DRAW_BB_LABELS = True
DEFAULT_DRAW_BB_SOURCE = True
DEFAULT_DRAW_PERSON_LIKE_ONLY = False
DEFAULT_MAX_BB_DEBUG_IMAGES = None
DEFAULT_BB_THICKNESS = 1
DEFAULT_BB_TEXT_SCALE = 0.35

DEFAULT_FINAL_DATASET_SIZE = 3300
DEFAULT_PRIORITY_PERSON_COUNT = 1600

DEFAULT_CROP_SIZE = 256
DEFAULT_NUM_CROPS_PER_IMAGE = 4
DEFAULT_DESIRED_NUM_CROPS = 4

DEFAULT_DUPLICATE_IOU_THRESHOLD = 0.50
DEFAULT_DUPLICATE_OVER_SMALLER_THRESHOLD = 0.80


# Person-like labels.
# These are used for crop scoring and crop prioritisation.
# They do NOT mean that only these categories are saved.
PERSON_LABELS = {
    "pedestrian",
    "sitting person",
    "person group",
    "person (other)",
    "rider",
    "person",
    "persongroup",
    "ridergroup",
}

# Group labels are handled carefully during duplicate removal.
# A person group should not automatically delete an individual pedestrian box.
PERSON_GROUP_LABELS = {
    "person group",
    "persongroup",
    "ridergroup",
}

# Labels to exclude from final crop annotations.
EXCLUDE_LABELS = {"ego vehicle", "out of roi"}

# Prefer CityPersons boxes over gtCoarse boxes when they describe the same object.
SOURCE_PRIORITY = {
    "citypersons": 2,
    "gtcoarse": 1,
    "unknown": 0,
}

SOURCE_ABBREVIATION = {
    "citypersons": "CP",
    "gtcoarse": "GC",
    "unknown": "UNK",
}

# COCO-like category data.
category_id_map = {}
category_counter = 1

# Runtime counters.
duplicate_annotations_removed = 0

# Runtime-configured globals used by helper functions.
CROP_SIZE = DEFAULT_CROP_SIZE
NUM_CROPS_PER_IMAGE = DEFAULT_NUM_CROPS_PER_IMAGE
DESIRED_NUM_CROPS = DEFAULT_DESIRED_NUM_CROPS
DUPLICATE_IOU_THRESHOLD = DEFAULT_DUPLICATE_IOU_THRESHOLD
DUPLICATE_OVER_SMALLER_THRESHOLD = DEFAULT_DUPLICATE_OVER_SMALLER_THRESHOLD

DRAW_PERSON_LIKE_ONLY = DEFAULT_DRAW_PERSON_LIKE_ONLY
DRAW_BB_LABELS = DEFAULT_DRAW_BB_LABELS
DRAW_BB_SOURCE = DEFAULT_DRAW_BB_SOURCE
BB_THICKNESS = DEFAULT_BB_THICKNESS
BB_TEXT_SCALE = DEFAULT_BB_TEXT_SCALE


# ================================
# ARGUMENTS
# ================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Create Cityscapes--Pedestrian 256x256 crops with bounding boxes "
            "from local Cityscapes, CityPersons, and gtCoarse files."
        )
    )

    parser.add_argument(
        "--cityscapes-root",
        default=os.environ.get("CITYSCAPES_ROOT"),
        help=(
            "Path to the local Cityscapes root. Expected default layout includes "
            "leftImg8bit_blurred/leftImg8bit_blurred, "
            "gtBbox_cityPersons_trainval/gtBboxCityPersons, and "
            "gtCoarse/gtCoarse. You may also set CITYSCAPES_ROOT."
        ),
    )

    parser.add_argument(
        "--images-dir",
        default=os.environ.get("CITYSCAPES_IMAGES_DIR"),
        help=(
            "Optional override for the local Cityscapes blurred image root. "
            "Default: CITYSCAPES_ROOT/leftImg8bit_blurred/leftImg8bit_blurred."
        ),
    )

    parser.add_argument(
        "--bbox-dir",
        default=os.environ.get("CITYSCAPES_BBOX_DIR"),
        help=(
            "Optional override for the CityPersons bounding-box annotation root. "
            "Default: CITYSCAPES_ROOT/gtBbox_cityPersons_trainval/gtBboxCityPersons."
        ),
    )

    parser.add_argument(
        "--coarse-dir",
        default=os.environ.get("CITYSCAPES_COARSE_DIR"),
        help=(
            "Optional override for the gtCoarse annotation root. "
            "Default: CITYSCAPES_ROOT/gtCoarse/gtCoarse."
        ),
    )

    parser.add_argument(
        "--output-dir",
        default=os.environ.get("CITYSCAPES_OUTPUT_DIR"),
        help=(
            "Output directory for processed crops and annotations. "
            "Default: CITYSCAPES_ROOT/processed."
        ),
    )

    parser.add_argument(
        "--splits",
        nargs="+",
        default=DEFAULT_SPLITS,
        choices=["train", "val"],
        help="Splits to process. Default: train val.",
    )

    parser.add_argument(
        "--crop-size",
        type=int,
        default=DEFAULT_CROP_SIZE,
        help="Square crop size in pixels. Default: 256.",
    )

    parser.add_argument(
        "--num-crops-per-image",
        type=int,
        default=DEFAULT_NUM_CROPS_PER_IMAGE,
        help="Maximum candidate crops retained per source image. Default: 4.",
    )

    parser.add_argument(
        "--desired-num-crops",
        type=int,
        default=DEFAULT_DESIRED_NUM_CROPS,
        help="Incremental crop passes per base image. Default: 4.",
    )

    parser.add_argument(
        "--final-dataset-size",
        type=int,
        default=DEFAULT_FINAL_DATASET_SIZE,
        help="Final number of selected crops. Default: 3300.",
    )

    parser.add_argument(
        "--priority-person-count",
        type=int,
        default=DEFAULT_PRIORITY_PERSON_COUNT,
        help=(
            "Number of highest person-count crops to keep before random fill. "
            "Default: 1600."
        ),
    )

    parser.add_argument(
        "--duplicate-iou-threshold",
        type=float,
        default=DEFAULT_DUPLICATE_IOU_THRESHOLD,
        help="IoU threshold for cross-source duplicate removal. Default: 0.50.",
    )

    parser.add_argument(
        "--duplicate-over-smaller-threshold",
        type=float,
        default=DEFAULT_DUPLICATE_OVER_SMALLER_THRESHOLD,
        help=(
            "Intersection-over-smaller-box threshold for cross-source duplicate "
            "removal. Default: 0.80."
        ),
    )

    parser.add_argument(
        "--draw-bb-debug",
        dest="draw_bb_debug",
        action="store_true",
        default=DEFAULT_DRAW_BB_DEBUG,
        help="Write debug images with bounding boxes. This is the default.",
    )

    parser.add_argument(
        "--no-draw-bb-debug",
        dest="draw_bb_debug",
        action="store_false",
        help="Do not write debug images with bounding boxes.",
    )

    parser.add_argument(
        "--clear-bb-dir",
        dest="clear_bb_dir_on_run",
        action="store_true",
        default=DEFAULT_CLEAR_BB_DIR_ON_RUN,
        help="Clear the debug BB directory before running. This is the default.",
    )

    parser.add_argument(
        "--no-clear-bb-dir",
        dest="clear_bb_dir_on_run",
        action="store_false",
        help="Do not clear the debug BB directory before running.",
    )

    parser.add_argument(
        "--draw-bb-labels",
        dest="draw_bb_labels",
        action="store_true",
        default=DEFAULT_DRAW_BB_LABELS,
        help="Draw labels on debug bounding boxes. This is the default.",
    )

    parser.add_argument(
        "--no-draw-bb-labels",
        dest="draw_bb_labels",
        action="store_false",
        help="Do not draw labels on debug bounding boxes.",
    )

    parser.add_argument(
        "--draw-bb-source",
        dest="draw_bb_source",
        action="store_true",
        default=DEFAULT_DRAW_BB_SOURCE,
        help="Draw source labels such as CP/GC on debug boxes. This is the default.",
    )

    parser.add_argument(
        "--no-draw-bb-source",
        dest="draw_bb_source",
        action="store_false",
        help="Do not draw source labels on debug boxes.",
    )

    parser.add_argument(
        "--draw-person-like-only",
        action="store_true",
        default=DEFAULT_DRAW_PERSON_LIKE_ONLY,
        help="Only draw pedestrian/rider/person-like boxes in debug images.",
    )

    parser.add_argument(
        "--max-bb-debug-images",
        type=int,
        default=DEFAULT_MAX_BB_DEBUG_IMAGES,
        help="Optional maximum number of debug images to save.",
    )

    parser.add_argument(
        "--bb-thickness",
        type=int,
        default=DEFAULT_BB_THICKNESS,
        help="Bounding-box line thickness for debug images. Default: 1.",
    )

    parser.add_argument(
        "--bb-text-scale",
        type=float,
        default=DEFAULT_BB_TEXT_SCALE,
        help="Text scale for debug labels. Default: 0.35.",
    )

    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed for final random crop selection. Default: 42.",
    )

    return parser.parse_args()


def resolve_paths(args):
    if not args.cityscapes_root and (
        not args.images_dir or not args.bbox_dir or not args.coarse_dir
    ):
        raise RuntimeError(
            "Provide --cityscapes-root or provide --images-dir, --bbox-dir, "
            "and --coarse-dir explicitly. You may also set CITYSCAPES_ROOT."
        )

    cityscapes_root = (
        os.path.abspath(args.cityscapes_root)
        if args.cityscapes_root
        else None
    )

    images_dir = (
        os.path.abspath(args.images_dir)
        if args.images_dir
        else os.path.join(cityscapes_root, "leftImg8bit_blurred", "leftImg8bit_blurred")
    )

    bbox_dir = (
        os.path.abspath(args.bbox_dir)
        if args.bbox_dir
        else os.path.join(
            cityscapes_root,
            "gtBbox_cityPersons_trainval",
            "gtBboxCityPersons",
        )
    )

    coarse_dir = (
        os.path.abspath(args.coarse_dir)
        if args.coarse_dir
        else os.path.join(cityscapes_root, "gtCoarse", "gtCoarse")
    )

    output_dir = (
        os.path.abspath(args.output_dir)
        if args.output_dir
        else os.path.join(cityscapes_root, "processed")
    )

    return cityscapes_root, images_dir, bbox_dir, coarse_dir, output_dir


def validate_inputs(images_dir, bbox_dir, coarse_dir, splits):
    for path_name, path_value in [
        ("images_dir", images_dir),
        ("bbox_dir", bbox_dir),
        ("coarse_dir", coarse_dir),
    ]:
        if not os.path.isdir(path_value):
            raise FileNotFoundError(f"{path_name} does not exist: {path_value}")

    for split in splits:
        split_images = os.path.join(images_dir, split)
        split_bbox = os.path.join(bbox_dir, split)
        split_coarse = os.path.join(coarse_dir, split)

        if not os.path.isdir(split_images):
            raise FileNotFoundError(
                f"Image split directory does not exist for '{split}': {split_images}"
            )

        if not os.path.isdir(split_bbox):
            raise FileNotFoundError(
                f"CityPersons bbox split directory does not exist for '{split}': {split_bbox}"
            )

        if not os.path.isdir(split_coarse):
            raise FileNotFoundError(
                f"gtCoarse split directory does not exist for '{split}': {split_coarse}"
            )


def import_cv2():
    try:
        import cv2 as cv2_module
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required for this script. Install it with: "
            "pip install opencv-python"
        ) from exc

    return cv2_module


# ================================
# HELPERS
# ================================

def update_category_map(label):
    """Add label to global category map if not present."""
    global category_counter
    if label not in category_id_map:
        category_id_map[label] = category_counter
        category_counter += 1


def polygon_to_bbox(poly):
    """Convert a polygon [[x,y], ...] to [x,y,w,h]."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]


def bbox_area(bbox):
    """Return area of [x,y,w,h]."""
    if bbox is None or len(bbox) != 4:
        return 0.0
    _, _, w, h = bbox
    return max(0.0, float(w)) * max(0.0, float(h))


def bbox_intersection_area(b1, b2):
    """Return intersection area of two [x,y,w,h] boxes."""
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2

    left = max(float(x1), float(x2))
    top = max(float(y1), float(y2))
    right = min(float(x1) + float(w1), float(x2) + float(w2))
    bottom = min(float(y1) + float(h1), float(y2) + float(h2))

    inter_w = max(0.0, right - left)
    inter_h = max(0.0, bottom - top)
    return inter_w * inter_h


def bbox_iou(b1, b2):
    """Return IoU of two [x,y,w,h] boxes."""
    inter = bbox_intersection_area(b1, b2)
    area1 = bbox_area(b1)
    area2 = bbox_area(b2)
    union = area1 + area2 - inter
    if union <= 0:
        return 0.0
    return inter / union


def overlap_over_smaller_box(b1, b2):
    """Return intersection divided by the smaller box area."""
    inter = bbox_intersection_area(b1, b2)
    smaller = min(bbox_area(b1), bbox_area(b2))
    if smaller <= 0:
        return 0.0
    return inter / smaller


def labels_are_duplicate_compatible(label_a, label_b):
    """
    Decide whether two labels are allowed to be considered duplicates.

    Exact label matches are compatible.
    Person-like labels are also compatible, e.g. CityPersons 'pedestrian'
    and gtCoarse 'person'.

    However, an individual person label and a group label are NOT treated as
    duplicates unless the labels are exactly the same. This avoids deleting
    individual pedestrians just because a larger 'person group' polygon overlaps them.
    """
    la = str(label_a).strip().lower()
    lb = str(label_b).strip().lower()

    if la == lb:
        return True

    if la in PERSON_LABELS and lb in PERSON_LABELS:
        a_is_group = la in PERSON_GROUP_LABELS
        b_is_group = lb in PERSON_GROUP_LABELS

        # Do not treat individual-vs-group as duplicate.
        if a_is_group != b_is_group:
            return False

        # Both are individual person-like labels, or both are group-like labels.
        return True

    return False


def objects_are_likely_duplicates(obj_a, obj_b):
    """Return True if two cross-source objects likely describe the same real object."""
    source_a = obj_a.get("_source", "unknown")
    source_b = obj_b.get("_source", "unknown")

    # Only remove duplicates across CityPersons vs gtCoarse.
    if source_a == source_b:
        return False

    label_a = obj_a.get("label", "")
    label_b = obj_b.get("label", "")
    if not labels_are_duplicate_compatible(label_a, label_b):
        return False

    box_a = obj_a.get("bbox", [0, 0, 0, 0])
    box_b = obj_b.get("bbox", [0, 0, 0, 0])
    if bbox_area(box_a) <= 0 or bbox_area(box_b) <= 0:
        return False

    iou = bbox_iou(box_a, box_b)
    overlap_smaller = overlap_over_smaller_box(box_a, box_b)

    return (
        iou >= DUPLICATE_IOU_THRESHOLD or
        overlap_smaller >= DUPLICATE_OVER_SMALLER_THRESHOLD
    )


def deduplicate_cross_source_objects(objects):
    """
    Remove likely duplicate objects after merging CityPersons and gtCoarse.

    The function prefers CityPersons over gtCoarse when two cross-source boxes
    strongly overlap and have compatible labels.
    """
    global duplicate_annotations_removed

    # Higher-priority sources are considered first, so CityPersons boxes are kept
    # before gtCoarse boxes when they overlap.
    sorted_objects = sorted(
        objects,
        key=lambda o: SOURCE_PRIORITY.get(o.get("_source", "unknown"), 0),
        reverse=True
    )

    kept = []
    for obj in sorted_objects:
        duplicate_found = False
        for existing in kept:
            if objects_are_likely_duplicates(obj, existing):
                duplicate_found = True
                duplicate_annotations_removed += 1
                break

        if not duplicate_found:
            kept.append(obj)

    return kept


def get_best_crops(img_w, img_h, objects, topN=4):
    """Return up to topN best 256x256 crops focusing on fully-covered PERSON_LABELS."""
    if img_w < CROP_SIZE or img_h < CROP_SIZE:
        return []

    person_boxes = []
    for obj in objects:
        lbl = str(obj.get("label", "")).strip().lower()
        if lbl in PERSON_LABELS and "bbox" in obj:
            x, y, w, h = obj["bbox"]
            if w > 0 and h > 0:
                person_boxes.append((x, y, w, h))

    if not person_boxes:
        return []

    stride_x = max(1, (img_w - CROP_SIZE) // 64 + 1)
    stride_y = max(1, (img_h - CROP_SIZE) // 64 + 1)

    candidates = []
    for i in range(stride_x + 1):
        cx = int((img_w - CROP_SIZE) * (i / stride_x))
        for j in range(stride_y + 1):
            cy = int((img_h - CROP_SIZE) * (j / stride_y))

            score = 0
            for bx, by, bw, bh in person_boxes:
                if (
                    bx >= cx and bx + bw <= cx + CROP_SIZE and
                    by >= cy and by + bh <= cy + CROP_SIZE
                ):
                    score += 1

            candidates.append((cx, cy, score))

    candidates.sort(key=lambda c: c[2], reverse=True)
    return [(int(cx), int(cy)) for (cx, cy, sc) in candidates[:topN]]


def color_for_category(category_id):
    """Return a deterministic BGR color for an OpenCV rectangle."""
    cid = int(category_id)
    blue = (37 * cid + 80) % 255
    green = (17 * cid + 140) % 255
    red = (29 * cid + 200) % 255
    return int(blue), int(green), int(red)


def draw_annotations_on_crop(image_bgr, annotations, id_to_label):
    """
    Draw final crop annotations onto a copy of image_bgr.

    The original training crop is not modified. This is only for visual inspection.
    """
    debug_img = image_bgr.copy()
    img_h, img_w = debug_img.shape[:2]

    for ann in annotations:
        cat_id = ann.get("category_id", -1)
        label = id_to_label.get(cat_id, str(cat_id))
        label_lower = str(label).strip().lower()

        if DRAW_PERSON_LIKE_ONLY and label_lower not in PERSON_LABELS:
            continue

        x, y, w, h = ann.get("bbox", [0, 0, 0, 0])
        x1 = max(0, min(img_w - 1, int(round(x))))
        y1 = max(0, min(img_h - 1, int(round(y))))
        x2 = max(0, min(img_w - 1, int(round(x + w))))
        y2 = max(0, min(img_h - 1, int(round(y + h))))

        if x2 <= x1 or y2 <= y1:
            continue

        color = color_for_category(cat_id)
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), color, BB_THICKNESS)

        if DRAW_BB_LABELS:
            text = str(label)
            if DRAW_BB_SOURCE:
                src = ann.get("_source", "unknown")
                text = f"{label} [{SOURCE_ABBREVIATION.get(src, src)}]"

            font = cv2.FONT_HERSHEY_SIMPLEX
            text_thickness = 1
            (text_w, text_h), baseline = cv2.getTextSize(text, font, BB_TEXT_SCALE, text_thickness)

            # Draw label above the box if possible, otherwise inside the top of the box.
            label_y_top = y1 - text_h - baseline - 4
            if label_y_top < 0:
                label_y_top = y1
                text_y = y1 + text_h + 2
            else:
                text_y = y1 - baseline - 2

            label_x2 = min(img_w - 1, x1 + text_w + 4)
            label_y2 = min(img_h - 1, label_y_top + text_h + baseline + 4)

            cv2.rectangle(debug_img, (x1, label_y_top), (label_x2, label_y2), color, -1)
            cv2.putText(
                debug_img,
                text,
                (x1 + 2, text_y),
                font,
                BB_TEXT_SCALE,
                (255, 255, 255),
                text_thickness,
                cv2.LINE_AA
            )

    return debug_img




# ================================
# MAIN
# ================================

def main():
    global cv2
    global category_id_map
    global category_counter
    global duplicate_annotations_removed
    global CROP_SIZE
    global NUM_CROPS_PER_IMAGE
    global DESIRED_NUM_CROPS
    global DUPLICATE_IOU_THRESHOLD
    global DUPLICATE_OVER_SMALLER_THRESHOLD
    global DRAW_PERSON_LIKE_ONLY
    global DRAW_BB_LABELS
    global DRAW_BB_SOURCE
    global BB_THICKNESS
    global BB_TEXT_SCALE

    args = parse_args()

    random.seed(args.random_seed)

    (
        CITYSCAPES_ROOT,
        IMAGES_DIR,
        BBOX_DIR,
        COARSE_DIR,
        OUTPUT_DIR,
    ) = resolve_paths(args)

    validate_inputs(
        images_dir=IMAGES_DIR,
        bbox_dir=BBOX_DIR,
        coarse_dir=COARSE_DIR,
        splits=args.splits,
    )

    cv2 = import_cv2()

    SPLITS = args.splits
    OUTPUT_IMAGES_DIR = os.path.join(OUTPUT_DIR, "cropped_images")
    OUTPUT_JSON = os.path.join(OUTPUT_DIR, "cropped_annotations.json")
    OUTPUT_BB_DIR = os.path.join(OUTPUT_DIR, "BB")

    DRAW_BB_DEBUG = args.draw_bb_debug
    CLEAR_BB_DIR_ON_RUN = args.clear_bb_dir_on_run
    MAX_BB_DEBUG_IMAGES = args.max_bb_debug_images

    FINAL_DATASET_SIZE = args.final_dataset_size
    PRIORITY_PERSON_COUNT = args.priority_person_count

    CROP_SIZE = args.crop_size
    NUM_CROPS_PER_IMAGE = args.num_crops_per_image
    DESIRED_NUM_CROPS = args.desired_num_crops

    DUPLICATE_IOU_THRESHOLD = args.duplicate_iou_threshold
    DUPLICATE_OVER_SMALLER_THRESHOLD = args.duplicate_over_smaller_threshold

    DRAW_PERSON_LIKE_ONLY = args.draw_person_like_only
    DRAW_BB_LABELS = args.draw_bb_labels
    DRAW_BB_SOURCE = args.draw_bb_source
    BB_THICKNESS = args.bb_thickness
    BB_TEXT_SCALE = args.bb_text_scale

    category_id_map = {}
    category_counter = 1
    duplicate_annotations_removed = 0

    os.makedirs(OUTPUT_IMAGES_DIR, exist_ok=True)

    if DRAW_BB_DEBUG:
        if CLEAR_BB_DIR_ON_RUN and os.path.isdir(OUTPUT_BB_DIR):
            shutil.rmtree(OUTPUT_BB_DIR)
        os.makedirs(OUTPUT_BB_DIR, exist_ok=True)

    print("Cityscapes--Pedestrian crop generation")
    print("======================================")
    print(f"Cityscapes root:        {CITYSCAPES_ROOT or '[custom paths]'}")
    print(f"Images dir:             {IMAGES_DIR}")
    print(f"CityPersons bbox dir:   {BBOX_DIR}")
    print(f"gtCoarse dir:           {COARSE_DIR}")
    print(f"Output dir:             {OUTPUT_DIR}")
    print(f"Splits:                 {SPLITS}")
    print(f"Crop size:              {CROP_SIZE}")
    print(f"Final dataset size:     {FINAL_DATASET_SIZE}")
    print(f"Draw BB debug images:   {DRAW_BB_DEBUG}")

    # ================================
    # 1) Build category map
    # ================================
    print("Building category map from CityPersons + gtCoarse...")
    for split in SPLITS:
        sub_bbox_dir = os.path.join(BBOX_DIR, split)
        sub_coarse_dir = os.path.join(COARSE_DIR, split)
        if not (os.path.isdir(sub_bbox_dir) and os.path.isdir(sub_coarse_dir)):
            continue

        for city in sorted(os.listdir(sub_bbox_dir)):
            cb_dir = os.path.join(sub_bbox_dir, city)
            if not os.path.isdir(cb_dir):
                continue

            for annf in sorted(os.listdir(cb_dir)):
                if annf.endswith(".json"):
                    with open(os.path.join(cb_dir, annf), "r") as f:
                        data = json.load(f)
                    for o in data.get("objects", []):
                        update_category_map(o.get("label", ""))

            cc_dir = os.path.join(sub_coarse_dir, city)
            if os.path.isdir(cc_dir):
                for annf in sorted(os.listdir(cc_dir)):
                    if annf.endswith(".json"):
                        with open(os.path.join(cc_dir, annf), "r") as f:
                            data = json.load(f)
                        for o in data.get("objects", []):
                            update_category_map(o.get("label", ""))

    print(f"Found {len(category_id_map)} categories in total.")
    id_to_label = {v: k for (k, v) in category_id_map.items()}

    # ================================
    # 2) Generate up to 4 crops per image
    # ================================
    print("\nGenerating up to 4 best crops from each image in memory...")

    all_crops = []

    for split in SPLITS:
        images_dir = os.path.join(IMAGES_DIR, split)
        sub_bbox = os.path.join(BBOX_DIR, split)
        sub_coarse = os.path.join(COARSE_DIR, split)
        if not (os.path.isdir(images_dir) and os.path.isdir(sub_bbox) and os.path.isdir(sub_coarse)):
            print(f"Skipping {split}: missing data.")
            continue

        city_list = sorted(os.listdir(images_dir))
        for city in tqdm(city_list, desc=f"Processing {split}"):
            city_img_dir = os.path.join(images_dir, city)
            cb_dir = os.path.join(sub_bbox, city)
            cc_dir = os.path.join(sub_coarse, city)
            if not (os.path.isdir(city_img_dir) and os.path.isdir(cb_dir) and os.path.isdir(cc_dir)):
                continue

            image_files = [f for f in sorted(os.listdir(city_img_dir)) if f.endswith(".jpg")]
            for imgf in image_files:
                base_name = imgf.replace("_leftImg8bit_blurred.jpg", "")
                bbox_json = base_name + "_gtBboxCityPersons.json"
                coarse_json = base_name + "_gtCoarse_polygons.json"
                pathB = os.path.join(cb_dir, bbox_json)
                pathC = os.path.join(cc_dir, coarse_json)

                if not (os.path.isfile(pathB) or os.path.isfile(pathC)):
                    continue

                img_path = os.path.join(city_img_dir, imgf)
                image = cv2.imread(img_path)
                if image is None:
                    continue
                H, W, _ = image.shape

                # Gather objects and tag their source.
                objects = []
                if os.path.isfile(pathB):
                    with open(pathB, "r") as f:
                        data = json.load(f)
                    for obj in data.get("objects", []):
                        obj_copy = dict(obj)
                        obj_copy["_source"] = "citypersons"
                        objects.append(obj_copy)

                if os.path.isfile(pathC):
                    with open(pathC, "r") as f:
                        data = json.load(f)
                    for obj in data.get("objects", []):
                        obj_copy = dict(obj)
                        obj_copy["_source"] = "gtcoarse"
                        objects.append(obj_copy)

                # Convert polygons to bboxes and set category IDs.
                prepared_objects = []
                for obj in objects:
                    lbl = obj.get("label", "")
                    cid = category_id_map.get(lbl, 999)
                    obj["category_id"] = cid

                    if "polygon" in obj:
                        obj["bbox"] = polygon_to_bbox(obj["polygon"])

                    if "bbox" not in obj:
                        obj["bbox"] = [0, 0, 0, 0]

                    x, y, w, h = obj["bbox"]
                    if w > 0 and h > 0:
                        prepared_objects.append(obj)

                # Remove likely duplicates between CityPersons and gtCoarse before crop scoring.
                objects = deduplicate_cross_source_objects(prepared_objects)

                # Find best up to 4 crops.
                best = get_best_crops(W, H, objects, topN=NUM_CROPS_PER_IMAGE)
                if not best:
                    continue

                crop_entries = []
                for (cx, cy) in best:
                    crop_anns = []

                    for obj in objects:
                        x, y, w, h = obj["bbox"]
                        if w <= 0 or h <= 0:
                            continue

                        # Partial overlap with crop.
                        left = x
                        right = x + w
                        top = y
                        bottom = y + h

                        c_left = cx
                        c_right = cx + CROP_SIZE
                        c_top = cy
                        c_bot = cy + CROP_SIZE

                        inter_left = max(left, c_left)
                        inter_right = min(right, c_right)
                        inter_top = max(top, c_top)
                        inter_bottom = min(bottom, c_bot)

                        inter_w = inter_right - inter_left
                        inter_h = inter_bottom - inter_top

                        if inter_w > 0 and inter_h > 0:
                            adj_x = inter_left - c_left
                            adj_y = inter_top - c_top
                            cat_id = obj["category_id"]

                            crop_anns.append({
                                "category_id": cat_id,
                                "bbox": [int(adj_x), int(adj_y), int(inter_w), int(inter_h)],
                                "area": int(inter_w * inter_h),
                                "iscrowd": 0,
                                "_source": obj.get("_source", "unknown")
                            })

                    if crop_anns:
                        crop_entries.append({
                            "cx": cx,
                            "cy": cy,
                            "annotations": crop_anns
                        })

                if crop_entries:
                    all_crops.append({
                        "base_img": base_name,
                        "split": split,
                        "city": city,
                        "width": W,
                        "height": H,
                        "crops": crop_entries
                    })

    print(f"Total base images with candidate crops: {len(all_crops)}")
    print(f"Removed likely duplicate cross-source annotations: {duplicate_annotations_removed}")

    # ================================
    # 3) Filter out excluded labels, remove crops with fewer than 4 boxes, group by base
    # ================================
    print("\nFiltering and grouping by base image name...")

    grouped_by_base = {}
    for item in all_crops:
        bimg = item["base_img"]
        sp = item["split"]
        cty = item["city"]
        ow = item["width"]
        oh = item["height"]

        new_crops = []
        for c in item["crops"]:
            filtered_anns = []
            for ann in c["annotations"]:
                lbl = id_to_label.get(ann["category_id"], "???")
                if lbl not in EXCLUDE_LABELS:
                    filtered_anns.append(ann)

            if len(filtered_anns) >= 4:
                cc = dict(c)
                cc["annotations"] = filtered_anns
                new_crops.append(cc)

        if new_crops:
            grouped_by_base[bimg] = {
                "split": sp,
                "city": cty,
                "width": ow,
                "height": oh,
                "crops": new_crops
            }

    print(f"Remaining bases with valid crops: {len(grouped_by_base)}")

    # ================================
    # 4) Sort and select final crops
    # ================================

    def count_person_likes(anns):
        count = 0
        for ann in anns:
            lbl = str(id_to_label.get(ann["category_id"], "???")).strip().lower()
            if lbl in PERSON_LABELS:
                count += 1
        return count


    for bimg, data in grouped_by_base.items():
        arr = data["crops"]
        arr.sort(key=lambda c: count_person_likes(c["annotations"]), reverse=True)

    # Incremental approach:
    # pass k=1 -> top 1 crop from each base
    # pass k=2 -> top 2 from each base, etc.
    all_crops_after_incremental = []

    for k in range(1, DESIRED_NUM_CROPS + 1):
        for bimg, rec in grouped_by_base.items():
            arr = rec["crops"]
            if len(arr) >= k:
                chosen = arr[k - 1]
                all_crops_after_incremental.append({
                    "base_img": bimg,
                    "split": rec["split"],
                    "city": rec["city"],
                    "width": rec["width"],
                    "height": rec["height"],
                    "crop_x": chosen["cx"],
                    "crop_y": chosen["cy"],
                    "annotations": chosen["annotations"]
                })

        if len(all_crops_after_incremental) >= FINAL_DATASET_SIZE:
            break

    print(f"After incremental approach, total crops: {len(all_crops_after_incremental)}")


    def count_person_in_crop(c):
        return sum(
            1
            for ann in c["annotations"]
            if str(id_to_label.get(ann["category_id"], "")).strip().lower() in PERSON_LABELS
        )


    all_crops_after_incremental.sort(key=count_person_in_crop, reverse=True)

    top_person = all_crops_after_incremental[:PRIORITY_PERSON_COUNT]
    leftover = all_crops_after_incremental[PRIORITY_PERSON_COUNT:]
    selected = list(top_person)

    if len(selected) < FINAL_DATASET_SIZE:
        needed = FINAL_DATASET_SIZE - len(selected)
        random.shuffle(leftover)
        selected.extend(leftover[:needed])

    if len(selected) > FINAL_DATASET_SIZE:
        selected = selected[:FINAL_DATASET_SIZE]

    print(f"Final selected crops: {len(selected)}")

    # ================================
    # 5) Write images, optional BB debug images, and build COCO JSON
    # ================================
    final_images = []
    final_annotations = []
    image_id = 1
    annotation_id = 1
    debug_images_saved = 0

    for crop in tqdm(selected, desc="Saving final crops"):
        sp = crop["split"]
        cty = crop["city"]
        bimg = crop["base_img"]
        cx = crop["crop_x"]
        cy = crop["crop_y"]

        img_file = f"{bimg}_leftImg8bit_blurred.jpg"
        orig_path = os.path.join(IMAGES_DIR, sp, cty, img_file)
        orig = cv2.imread(orig_path)
        if orig is None:
            continue

        crop_img = orig[cy:cy + CROP_SIZE, cx:cx + CROP_SIZE]
        if crop_img.shape[0] != CROP_SIZE or crop_img.shape[1] != CROP_SIZE:
            continue

        out_name = f"{bimg}_crop_{image_id}.jpg"
        out_path = os.path.join(OUTPUT_IMAGES_DIR, out_name)
        cv2.imwrite(out_path, crop_img)

        # Optional debug image with bounding boxes drawn.
        if DRAW_BB_DEBUG:
            if MAX_BB_DEBUG_IMAGES is None or debug_images_saved < MAX_BB_DEBUG_IMAGES:
                bb_img = draw_annotations_on_crop(crop_img, crop["annotations"], id_to_label)
                bb_out_path = os.path.join(OUTPUT_BB_DIR, out_name)
                cv2.imwrite(bb_out_path, bb_img)
                debug_images_saved += 1

        final_images.append({
            "id": image_id,
            "file_name": out_name,
            "width": CROP_SIZE,
            "height": CROP_SIZE
        })

        for ann in crop["annotations"]:
            # Keep the final COCO JSON clean. Do not write debug-only keys such as _source.
            new_ann = {
                "id": annotation_id,
                "image_id": image_id,
                "category_id": ann["category_id"],
                "bbox": ann["bbox"],
                "area": ann["area"],
                "iscrowd": ann.get("iscrowd", 0)
            }
            annotation_id += 1
            final_annotations.append(new_ann)

        image_id += 1

    final_coco = {
        "info": {
            "description": "Cityscapes Crops Filtered with Duplicate Removal and Optional BB Debug Images",
            "version": "1.1",
            "year": 2023,
            "contributor": "Your Name",
            "date_created": "2023-XX-XX"
        },
        "images": final_images,
        "annotations": final_annotations,
        "categories": [
            {"id": cid, "name": lbl}
            for lbl, cid in category_id_map.items()
        ]
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(final_coco, f, indent=4)

    print(f"\nAll done! {len(final_images)} final images saved to: {OUTPUT_IMAGES_DIR}")
    print(f"{len(final_annotations)} annotations saved to: {OUTPUT_JSON}")
    print(f"Likely duplicate cross-source annotations removed: {duplicate_annotations_removed}")

    if DRAW_BB_DEBUG:
        print(f"{debug_images_saved} bounding-box debug images saved to: {OUTPUT_BB_DIR}")
    else:
        print("Bounding-box debug image output is disabled. Set DRAW_BB_DEBUG = True to enable it.")

if __name__ == "__main__":
    main()
