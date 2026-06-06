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

DEFAULT_SPLITS = ["train", "val"]

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
            "Draw YOLO bounding boxes on locally reconstructed COCO "
            "PottedPlant crop images for visual debugging."
        )
    )

    parser.add_argument(
        "--coco-root",
        default=os.environ.get("COCO_ROOT"),
        help=(
            "Path to the local COCO dataset root. The default cropped source "
            "folder is COCO_ROOT/YOLO_pottedplant_cropped. You may also set "
            "the COCO_ROOT environment variable."
        ),
    )

    parser.add_argument(
        "--source-dir",
        default=os.environ.get("COCO_CROPPED_YOLO_ROOT"),
        help=(
            "Path to the local cropped YOLO potted-plant dataset produced by "
            "step 02. Default: COCO_ROOT/YOLO_pottedplant_cropped. You may "
            "also set COCO_CROPPED_YOLO_ROOT."
        ),
    )

    parser.add_argument(
        "--bb-root",
        default=os.environ.get("COCO_BB_DEBUG_ROOT"),
        help=(
            "Output directory for debug images with bounding boxes. "
            "Default: SOURCE_DIR/BB. You may also set COCO_BB_DEBUG_ROOT."
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
        "--max-images-to-draw",
        type=int,
        default=None,
        help="Optional maximum number of images to draw per split.",
    )

    parser.add_argument(
        "--draw-only-class-ids",
        nargs="+",
        type=int,
        default=None,
        help="Optional list of class IDs to draw. Default: draw all classes.",
    )

    parser.add_argument(
        "--clear-bb-folder",
        dest="clear_bb_folder_on_run",
        action="store_true",
        default=DEFAULT_CLEAR_BB_FOLDER_ON_RUN,
        help="Clear the debug BB output folder before running. This is the default.",
    )

    parser.add_argument(
        "--no-clear-bb-folder",
        dest="clear_bb_folder_on_run",
        action="store_false",
        help="Do not clear the debug BB output folder before running.",
    )

    parser.add_argument(
        "--draw-labels",
        dest="draw_labels",
        action="store_true",
        default=DEFAULT_DRAW_LABELS,
        help="Draw class labels on boxes. This is the default.",
    )

    parser.add_argument(
        "--no-draw-labels",
        dest="draw_labels",
        action="store_false",
        help="Do not draw class labels on boxes.",
    )

    parser.add_argument(
        "--draw-confidence-if-present",
        action="store_true",
        default=DEFAULT_DRAW_CONFIDENCE_IF_PRESENT,
        help="Draw confidence values when label files contain a confidence column.",
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
        help="Save images even if their label file is missing. This is the default.",
    )

    parser.add_argument(
        "--no-save-images-without-labels",
        dest="save_images_without_labels",
        action="store_false",
        help="Skip images whose label file is missing.",
    )

    parser.add_argument(
        "--save-images-with-empty-labels",
        dest="save_images_with_empty_labels",
        action="store_true",
        default=DEFAULT_SAVE_IMAGES_WITH_EMPTY_LABELS,
        help="Save images even if their label file is empty. This is the default.",
    )

    parser.add_argument(
        "--no-save-images-with-empty-labels",
        dest="save_images_with_empty_labels",
        action="store_false",
        help="Skip images whose label file is empty.",
    )

    return parser.parse_args()


# ============================================================
# PATH RESOLUTION
# ============================================================

def resolve_paths(args):
    coco_root = None

    if args.coco_root:
        coco_root = Path(args.coco_root).expanduser().resolve()

    if args.source_dir:
        source_dir = Path(args.source_dir).expanduser().resolve()
    else:
        if coco_root is None:
            raise RuntimeError(
                "No source directory was provided. Pass --source-dir, "
                "or pass --coco-root, or set COCO_ROOT / COCO_CROPPED_YOLO_ROOT."
            )
        source_dir = coco_root / "YOLO_pottedplant_cropped"

    if args.bb_root:
        bb_root = Path(args.bb_root).expanduser().resolve()
    else:
        bb_root = source_dir / "BB"

    return source_dir, bb_root


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
# HELPERS
# ============================================================

def load_class_names(classes_file):
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


def parse_yolo_label_line(line):
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


def read_yolo_labels(label_path, draw_only_class_ids):
    annotations = []

    if not label_path.exists():
        return annotations

    with label_path.open("r", encoding="utf-8") as f:
        for line in f:
            ann = parse_yolo_label_line(line)

            if ann is None:
                continue

            if (
                draw_only_class_ids is not None
                and ann["class_id"] not in draw_only_class_ids
            ):
                continue

            annotations.append(ann)

    return annotations


def yolo_to_pixel_bbox(yolo_ann, img_width, img_height):
    x_center = yolo_ann["x_center"] * img_width
    y_center = yolo_ann["y_center"] * img_height
    box_width = yolo_ann["width"] * img_width
    box_height = yolo_ann["height"] * img_height

    x1 = x_center - box_width / 2.0
    y1 = y_center - box_height / 2.0
    x2 = x_center + box_width / 2.0
    y2 = y_center + box_height / 2.0

    x1 = max(0, min(int(round(x1)), img_width - 1))
    y1 = max(0, min(int(round(y1)), img_height - 1))
    x2 = max(0, min(int(round(x2)), img_width - 1))
    y2 = max(0, min(int(round(y2)), img_height - 1))

    if x2 <= x1 or y2 <= y1:
        return None

    return x1, y1, x2, y2


def get_color_for_class(class_id):
    palette = [
        (0, 255, 0),
        (255, 0, 0),
        (0, 0, 255),
        (0, 255, 255),
        (255, 0, 255),
        (255, 255, 0),
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
    font = cv2.FONT_HERSHEY_SIMPLEX

    text_size, baseline = cv2.getTextSize(
        text,
        font,
        text_scale,
        text_thickness,
    )

    text_width, text_height = text_size

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


def get_image_files(images_dir):
    image_files = []

    for file_name in os.listdir(images_dir):
        ext = os.path.splitext(file_name)[1].lower()

        if ext in IMAGE_EXTENSIONS:
            image_files.append(file_name)

    image_files.sort()

    return image_files


# ============================================================
# MAIN
# ============================================================

def main():
    args = parse_args()

    source_dir, bb_root = resolve_paths(args)

    images_root = source_dir / "images"
    labels_root = source_dir / "labels"
    classes_file = source_dir / "classes.txt"

    if not images_root.exists():
        raise FileNotFoundError(f"Images root does not exist: {images_root}")

    if not labels_root.exists():
        raise FileNotFoundError(f"Labels root does not exist: {labels_root}")

    cv2 = import_cv2()

    print("COCO PottedPlant bounding-box debug drawing")
    print("===========================================")
    print(f"Source dir:         {source_dir}")
    print(f"Images root:        {images_root}")
    print(f"Labels root:        {labels_root}")
    print(f"Classes file:       {classes_file}")
    print(f"BB output root:     {bb_root}")
    print(f"Splits:             {args.splits}")
    print(f"Clear BB folder:    {args.clear_bb_folder_on_run}")
    print(f"Draw labels:        {args.draw_labels}")
    print(f"Max images/split:   {args.max_images_to_draw}")

    print("\nLoading class names...")
    class_names = load_class_names(classes_file)

    if class_names:
        print("Classes found:")
        for class_id, class_name in class_names.items():
            print(f"  {class_id}: {class_name}")
    else:
        print("No classes loaded. Labels will show class IDs only.")

    if args.clear_bb_folder_on_run and bb_root.is_dir():
        print(f"Clearing old BB folder: {bb_root}")
        shutil.rmtree(bb_root)

    bb_root.mkdir(parents=True, exist_ok=True)

    for split in args.splits:
        print(f"\nProcessing split: {split}")

        images_dir = images_root / split
        labels_dir = labels_root / split
        bb_out_dir = bb_root / split

        if not images_dir.is_dir():
            print(f"Skipping missing images folder: {images_dir}")
            continue

        if not labels_dir.is_dir():
            print(f"Skipping missing labels folder: {labels_dir}")
            continue

        bb_out_dir.mkdir(parents=True, exist_ok=True)

        image_files = get_image_files(images_dir)

        if args.max_images_to_draw is not None:
            image_files = image_files[:args.max_images_to_draw]

        processed_images = 0
        saved_images = 0
        missing_label_files = 0
        empty_label_files = 0
        boxes_drawn = 0
        invalid_images = 0

        for image_file_name in tqdm(image_files, desc=f"Drawing YOLO BBs ({split})"):
            image_path = images_dir / image_file_name
            label_path = labels_dir / (Path(image_file_name).stem + ".txt")

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

                output_path = bb_out_dir / image_file_name
                cv2.imwrite(str(output_path), image)

                saved_images += 1
                processed_images += 1
                continue

            yolo_annotations = read_yolo_labels(
                label_path,
                args.draw_only_class_ids,
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
                        label_text = f"{class_id}: {class_name} {ann['confidence']:.2f}"
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

            output_path = bb_out_dir / image_file_name
            cv2.imwrite(str(output_path), image)

            saved_images += 1
            processed_images += 1

        print("")
        print(f"Finished split: {split}")
        print(f"Processed images: {processed_images}")
        print(f"Saved BB images: {saved_images}")
        print(f"Boxes drawn: {boxes_drawn}")
        print(f"Missing label files: {missing_label_files}")
        print(f"Empty label files: {empty_label_files}")
        print(f"Invalid/unreadable images: {invalid_images}")
        print(f"BB inspection folder: {bb_out_dir}")

    print("\nALL DONE.")


if __name__ == "__main__":
    main()