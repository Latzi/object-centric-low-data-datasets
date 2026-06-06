import argparse
import os
import shutil
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_CLEAR_BB_FOLDER_ON_RUN = True
DEFAULT_DRAW_LABELS = True
DEFAULT_DRAW_CONFIDENCE_IF_PRESENT = False

DEFAULT_BOX_THICKNESS = 2
DEFAULT_TEXT_SCALE = 0.45
DEFAULT_TEXT_THICKNESS = 1

DEFAULT_SAVE_IMAGES_WITHOUT_LABELS = True
DEFAULT_SAVE_IMAGES_WITH_EMPTY_LABELS = True

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


# ============================================================
# ARGUMENTS
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Draw YOLO bounding boxes on locally generated "
            "Cityscapes--Pedestrian YOLO images for visual debugging."
        )
    )

    parser.add_argument(
        "--processed-dir",
        default=os.environ.get("CITYSCAPES_PROCESSED_DIR"),
        help=(
            "Path to the local processed Cityscapes--Pedestrian folder. "
            "Default YOLO folder is PROCESSED_DIR/filtered_yolo. "
            "You may also set CITYSCAPES_PROCESSED_DIR."
        ),
    )

    parser.add_argument(
        "--yolo-dir",
        default=os.environ.get("CITYSCAPES_FILTERED_YOLO_DIR"),
        help=(
            "Path to the local YOLO folder created by script 03. "
            "Expected contents: images/, labels/, classes.txt. "
            "Default: PROCESSED_DIR/filtered_yolo. "
            "You may also set CITYSCAPES_FILTERED_YOLO_DIR."
        ),
    )

    parser.add_argument(
        "--images-dir",
        default=None,
        help=(
            "Optional explicit path to YOLO images. "
            "Default: YOLO_DIR/images."
        ),
    )

    parser.add_argument(
        "--labels-dir",
        default=None,
        help=(
            "Optional explicit path to YOLO labels. "
            "Default: YOLO_DIR/labels."
        ),
    )

    parser.add_argument(
        "--classes-file",
        default=None,
        help=(
            "Optional explicit path to classes.txt. "
            "Default: YOLO_DIR/classes.txt."
        ),
    )

    parser.add_argument(
        "--bb-output-dir",
        default=os.environ.get("CITYSCAPES_BB_DEBUG_DIR"),
        help=(
            "Output folder for inspection images with bounding boxes. "
            "Default: YOLO_DIR/BB. You may also set CITYSCAPES_BB_DEBUG_DIR."
        ),
    )

    parser.add_argument(
        "--clear-bb-folder",
        dest="clear_bb_folder_on_run",
        action="store_true",
        default=DEFAULT_CLEAR_BB_FOLDER_ON_RUN,
        help="Delete the old BB folder before creating new debug images. This is the default.",
    )

    parser.add_argument(
        "--no-clear-bb-folder",
        dest="clear_bb_folder_on_run",
        action="store_false",
        help="Do not delete the old BB folder before creating new debug images.",
    )

    parser.add_argument(
        "--draw-labels",
        dest="draw_labels",
        action="store_true",
        default=DEFAULT_DRAW_LABELS,
        help="Draw class name / class ID text above each box. This is the default.",
    )

    parser.add_argument(
        "--no-draw-labels",
        dest="draw_labels",
        action="store_false",
        help="Do not draw class labels above boxes.",
    )

    parser.add_argument(
        "--draw-confidence-if-present",
        action="store_true",
        default=DEFAULT_DRAW_CONFIDENCE_IF_PRESENT,
        help=(
            "Draw confidence values when label files contain a sixth confidence column. "
            "Standard dataset labels normally do not contain confidence values."
        ),
    )

    parser.add_argument(
        "--draw-only-class-ids",
        nargs="+",
        type=int,
        default=None,
        help=(
            "Optional list of class IDs to draw. "
            "Default: draw all classes."
        ),
    )

    parser.add_argument(
        "--max-images-to-draw",
        type=int,
        default=None,
        help=(
            "Optional maximum number of images to draw. "
            "Default: draw all images."
        ),
    )

    parser.add_argument(
        "--box-thickness",
        type=int,
        default=DEFAULT_BOX_THICKNESS,
        help="Bounding-box line thickness. Default: 2.",
    )

    parser.add_argument(
        "--text-scale",
        type=float,
        default=DEFAULT_TEXT_SCALE,
        help="Text scale for drawn labels. Default: 0.45.",
    )

    parser.add_argument(
        "--text-thickness",
        type=int,
        default=DEFAULT_TEXT_THICKNESS,
        help="Text thickness for drawn labels. Default: 1.",
    )

    parser.add_argument(
        "--save-images-without-labels",
        dest="save_images_without_labels",
        action="store_true",
        default=DEFAULT_SAVE_IMAGES_WITHOUT_LABELS,
        help=(
            "Save images even when there is no matching label file. "
            "The saved image will simply have no boxes. This is the default."
        ),
    )

    parser.add_argument(
        "--no-save-images-without-labels",
        dest="save_images_without_labels",
        action="store_false",
        help="Skip images that have no matching label file.",
    )

    parser.add_argument(
        "--save-images-with-empty-labels",
        dest="save_images_with_empty_labels",
        action="store_true",
        default=DEFAULT_SAVE_IMAGES_WITH_EMPTY_LABELS,
        help=(
            "Save images even when the label file exists but contains no boxes. "
            "This is the default."
        ),
    )

    parser.add_argument(
        "--no-save-images-with-empty-labels",
        dest="save_images_with_empty_labels",
        action="store_false",
        help="Skip images whose label file exists but contains no boxes.",
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

    if args.yolo_dir:
        yolo_dir = Path(args.yolo_dir).expanduser().resolve()
    else:
        if processed_dir is None:
            raise RuntimeError(
                "No YOLO directory was provided. Pass --yolo-dir, "
                "or pass --processed-dir, or set CITYSCAPES_FILTERED_YOLO_DIR "
                "or CITYSCAPES_PROCESSED_DIR."
            )

        yolo_dir = processed_dir / "filtered_yolo"

    if args.images_dir:
        yolo_images_dir = Path(args.images_dir).expanduser().resolve()
    else:
        yolo_images_dir = yolo_dir / "images"

    if args.labels_dir:
        yolo_labels_dir = Path(args.labels_dir).expanduser().resolve()
    else:
        yolo_labels_dir = yolo_dir / "labels"

    if args.classes_file:
        yolo_classes_file = Path(args.classes_file).expanduser().resolve()
    else:
        yolo_classes_file = yolo_dir / "classes.txt"

    if args.bb_output_dir:
        bb_output_dir = Path(args.bb_output_dir).expanduser().resolve()
    else:
        bb_output_dir = yolo_dir / "BB"

    return {
        "processed_dir": processed_dir,
        "yolo_dir": yolo_dir,
        "yolo_images_dir": yolo_images_dir,
        "yolo_labels_dir": yolo_labels_dir,
        "yolo_classes_file": yolo_classes_file,
        "bb_output_dir": bb_output_dir,
    }


def validate_inputs(paths):
    yolo_images_dir = paths["yolo_images_dir"]
    yolo_labels_dir = paths["yolo_labels_dir"]

    if not yolo_images_dir.is_dir():
        raise FileNotFoundError(
            f"Images folder not found: {yolo_images_dir}"
        )

    if not yolo_labels_dir.is_dir():
        raise FileNotFoundError(
            f"Labels folder not found: {yolo_labels_dir}"
        )


# ============================================================
# DEPENDENCY LOADING
# ============================================================

def import_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required for this script. Install it with: "
            "pip install opencv-python"
        ) from exc

    return cv2


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_class_names(classes_file):
    """
    Load YOLO class names from classes.txt.

    If classes.txt does not exist, class names will simply be class_0, class_1, etc.
    """
    if not classes_file.exists():
        print(f"Warning: classes.txt not found: {classes_file}")
        return {}

    class_names = {}

    with classes_file.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            name = line.strip()

            if name:
                class_names[idx] = name

    return class_names


def image_to_label_path(image_file_name, yolo_labels_dir):
    """
    Convert image filename to matching YOLO label filename.

    Example:
        abc.jpg -> abc.txt
    """
    base_name = os.path.splitext(os.path.basename(image_file_name))[0]
    return yolo_labels_dir / f"{base_name}.txt"


def parse_yolo_label_line(line):
    """
    Parse one YOLO annotation line.

    Expected format:
        class_id x_center y_center width height

    Optional format with confidence:
        class_id x_center y_center width height confidence

    All coordinates are normalized between 0 and 1.
    """
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

        confidence = None
        if len(parts) >= 6:
            confidence = float(parts[5])

        return {
            "class_id": class_id,
            "x_center": x_center,
            "y_center": y_center,
            "width": width,
            "height": height,
            "confidence": confidence,
        }

    except Exception:
        return None


def yolo_to_pixel_bbox(yolo_ann, img_width, img_height):
    """
    Convert YOLO normalized bbox to pixel bbox.

    YOLO:
        x_center_norm, y_center_norm, width_norm, height_norm

    Pixel:
        x1, y1, x2, y2
    """
    x_center = yolo_ann["x_center"] * img_width
    y_center = yolo_ann["y_center"] * img_height
    box_width = yolo_ann["width"] * img_width
    box_height = yolo_ann["height"] * img_height

    x1 = x_center - box_width / 2.0
    y1 = y_center - box_height / 2.0
    x2 = x_center + box_width / 2.0
    y2 = y_center + box_height / 2.0

    # Clip to image boundaries.
    x1 = max(0, min(int(round(x1)), img_width - 1))
    y1 = max(0, min(int(round(y1)), img_height - 1))
    x2 = max(0, min(int(round(x2)), img_width - 1))
    y2 = max(0, min(int(round(y2)), img_height - 1))

    if x2 <= x1 or y2 <= y1:
        return None

    return x1, y1, x2, y2


def get_color_for_class(class_id):
    """
    Return a repeatable BGR color for a class ID.

    OpenCV uses BGR, not RGB.
    """
    palette = [
        (0, 255, 0),      # green
        (255, 0, 0),      # blue
        (0, 0, 255),      # red
        (0, 255, 255),    # yellow
        (255, 0, 255),    # magenta
        (255, 255, 0),    # cyan
        (128, 255, 0),
        (255, 128, 0),
        (128, 0, 255),
        (0, 128, 255),
    ]

    return palette[class_id % len(palette)]


def draw_text_with_background(
    cv2,
    image,
    text,
    x,
    y,
    color,
    text_scale,
    text_thickness,
):
    """
    Draw readable text with a filled background.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX

    text_size, baseline = cv2.getTextSize(
        text,
        font,
        text_scale,
        text_thickness,
    )

    text_width, text_height = text_size

    # Keep text inside image.
    y_text_top = max(0, y - text_height - baseline - 4)
    y_text_bottom = max(text_height + baseline + 4, y)

    x_text_left = max(0, x)
    x_text_right = min(image.shape[1] - 1, x + text_width + 6)

    cv2.rectangle(
        image,
        (x_text_left, y_text_top),
        (x_text_right, y_text_bottom),
        color,
        thickness=-1,
    )

    cv2.putText(
        image,
        text,
        (x_text_left + 3, y_text_bottom - baseline - 2),
        font,
        text_scale,
        (255, 255, 255),
        text_thickness,
        cv2.LINE_AA,
    )


def read_yolo_labels(label_path, draw_only_class_ids):
    """
    Read all valid YOLO annotations from a label file.
    """
    annotations = []

    if not label_path.exists():
        return annotations

    with label_path.open("r", encoding="utf-8") as f:
        for line in f:
            ann = parse_yolo_label_line(line)

            if ann is None:
                continue

            if draw_only_class_ids is not None:
                if ann["class_id"] not in draw_only_class_ids:
                    continue

            annotations.append(ann)

    return annotations


def get_image_files(images_dir):
    """
    Return sorted image files from the YOLO images folder.
    """
    image_files = []

    for file_name in os.listdir(images_dir):
        ext = os.path.splitext(file_name)[1].lower()

        if ext in IMAGE_EXTENSIONS:
            image_files.append(file_name)

    image_files.sort()
    return image_files


# ============================================================
# MAIN SCRIPT
# ============================================================

def main():
    args = parse_args()
    paths = resolve_paths(args)

    validate_inputs(paths)

    cv2 = import_cv2()

    yolo_dir = paths["yolo_dir"]
    yolo_images_dir = paths["yolo_images_dir"]
    yolo_labels_dir = paths["yolo_labels_dir"]
    yolo_classes_file = paths["yolo_classes_file"]
    bb_output_dir = paths["bb_output_dir"]

    print("Cityscapes--Pedestrian YOLO bounding-box debug drawing")
    print("======================================================")
    print(f"YOLO dir:             {yolo_dir}")
    print(f"YOLO images dir:      {yolo_images_dir}")
    print(f"YOLO labels dir:      {yolo_labels_dir}")
    print(f"YOLO classes file:    {yolo_classes_file}")
    print(f"BB output dir:        {bb_output_dir}")
    print(f"Clear BB folder:      {args.clear_bb_folder_on_run}")
    print(f"Draw labels:          {args.draw_labels}")
    print(f"Max images to draw:   {args.max_images_to_draw}")

    print("")
    print("Loading class names...")

    class_names = load_class_names(yolo_classes_file)

    if class_names:
        print("Classes found:")
        for class_id, class_name in class_names.items():
            print(f"  {class_id}: {class_name}")
    else:
        print("No classes loaded. Labels will show class IDs only.")

    print("")

    if args.clear_bb_folder_on_run and bb_output_dir.is_dir():
        print(f"Clearing old BB folder: {bb_output_dir}")
        shutil.rmtree(bb_output_dir)

    bb_output_dir.mkdir(parents=True, exist_ok=True)

    image_files = get_image_files(yolo_images_dir)

    if args.max_images_to_draw is not None:
        image_files = image_files[:args.max_images_to_draw]

    print(f"Images to process: {len(image_files)}")
    print(f"Source images: {yolo_images_dir}")
    print(f"Source labels: {yolo_labels_dir}")
    print(f"BB output: {bb_output_dir}")
    print("")

    processed_images = 0
    saved_images = 0
    missing_label_files = 0
    empty_label_files = 0
    boxes_drawn = 0
    invalid_images = 0

    for image_file_name in tqdm(image_files, desc="Drawing YOLO BBs"):
        image_path = yolo_images_dir / image_file_name
        label_path = image_to_label_path(image_file_name, yolo_labels_dir)

        image = cv2.imread(str(image_path))

        if image is None:
            invalid_images += 1
            print(f"Warning: could not read image: {image_path}")
            continue

        img_height, img_width = image.shape[:2]

        label_exists = label_path.exists()

        if not label_exists:
            missing_label_files += 1

            if not args.save_images_without_labels:
                continue

            output_path = bb_output_dir / image_file_name
            cv2.imwrite(str(output_path), image)
            saved_images += 1
            processed_images += 1
            continue

        yolo_annotations = read_yolo_labels(
            label_path,
            draw_only_class_ids=args.draw_only_class_ids,
        )

        if len(yolo_annotations) == 0:
            empty_label_files += 1

            if not args.save_images_with_empty_labels:
                continue

        for ann in yolo_annotations:
            bbox = yolo_to_pixel_bbox(ann, img_width, img_height)

            if bbox is None:
                continue

            class_id = ann["class_id"]
            x1, y1, x2, y2 = bbox

            color = get_color_for_class(class_id)

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                color,
                thickness=args.box_thickness,
            )

            if args.draw_labels:
                class_name = class_names.get(class_id, f"class_{class_id}")

                if args.draw_confidence_if_present and ann["confidence"] is not None:
                    label_text = (
                        f"{class_id}: {class_name} {ann['confidence']:.2f}"
                    )
                else:
                    label_text = f"{class_id}: {class_name}"

                draw_text_with_background(
                    cv2=cv2,
                    image=image,
                    text=label_text,
                    x=x1,
                    y=y1,
                    color=color,
                    text_scale=args.text_scale,
                    text_thickness=args.text_thickness,
                )

            boxes_drawn += 1

        output_path = bb_output_dir / image_file_name
        cv2.imwrite(str(output_path), image)

        saved_images += 1
        processed_images += 1

    print("")
    print("Done.")
    print(f"Processed images: {processed_images}")
    print(f"Saved BB images: {saved_images}")
    print(f"Boxes drawn: {boxes_drawn}")
    print(f"Missing label files: {missing_label_files}")
    print(f"Empty label files: {empty_label_files}")
    print(f"Invalid/unreadable images: {invalid_images}")
    print(f"BB inspection folder: {bb_output_dir}")


if __name__ == "__main__":
    main()