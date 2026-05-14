import os
import cv2
import shutil
from tqdm import tqdm


# ============================================================
# PATH SETUP
# ============================================================

PROCESSED_DIR = r"C:\Users\richm\Downloads\Cityscapes\processed"

# This is the YOLO folder created by the previous COCO-to-YOLO script.
YOLO_DIR = os.path.join(PROCESSED_DIR, "filtered_yolo")

YOLO_IMAGES_DIR = os.path.join(YOLO_DIR, "images")
YOLO_LABELS_DIR = os.path.join(YOLO_DIR, "labels")
YOLO_CLASSES_FILE = os.path.join(YOLO_DIR, "classes.txt")

# Output folder for inspection images.
BB_OUTPUT_DIR = os.path.join(YOLO_DIR, "BB")


# ============================================================
# DRAWING SETTINGS
# ============================================================

# Delete the old BB folder before creating new debug images.
CLEAR_BB_FOLDER_ON_RUN = True

# Draw class name / class ID text above each box.
DRAW_LABELS = True

# Draw confidence? YOLO label files from your dataset do not contain confidence,
# so this should stay False unless your txt files have 6 columns.
DRAW_CONFIDENCE_IF_PRESENT = False

# Only draw these class IDs.
# Use None to draw all classes.
#
# Example:
#   DRAW_ONLY_CLASS_IDS = {0}
#
DRAW_ONLY_CLASS_IDS = None

# Limit how many images to draw.
# Use None to draw all images.
MAX_IMAGES_TO_DRAW = None

# Image extensions to process.
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

# Bounding-box drawing style.
BOX_THICKNESS = 2
TEXT_SCALE = 0.45
TEXT_THICKNESS = 1

# If True, save images even when there is no matching label file.
# The saved image will just have no boxes.
SAVE_IMAGES_WITHOUT_LABELS = True

# If True, save images even when the label file exists but has no boxes.
SAVE_IMAGES_WITH_EMPTY_LABELS = True


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_class_names(classes_file):
    """
    Load YOLO class names from classes.txt.

    If classes.txt does not exist, class names will simply be class_0, class_1, etc.
    """
    if not os.path.exists(classes_file):
        print(f"Warning: classes.txt not found: {classes_file}")
        return {}

    class_names = {}

    with open(classes_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            name = line.strip()
            if name:
                class_names[idx] = name

    return class_names


def image_to_label_path(image_file_name):
    """
    Convert image filename to matching YOLO label filename.

    Example:
        abc.jpg -> abc.txt
    """
    base_name = os.path.splitext(os.path.basename(image_file_name))[0]
    return os.path.join(YOLO_LABELS_DIR, base_name + ".txt")


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


def draw_text_with_background(image, text, x, y, color):
    """
    Draw readable text with a filled background.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX

    text_size, baseline = cv2.getTextSize(
        text,
        font,
        TEXT_SCALE,
        TEXT_THICKNESS
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
        thickness=-1
    )

    cv2.putText(
        image,
        text,
        (x_text_left + 3, y_text_bottom - baseline - 2),
        font,
        TEXT_SCALE,
        (255, 255, 255),
        TEXT_THICKNESS,
        cv2.LINE_AA
    )


def read_yolo_labels(label_path):
    """
    Read all valid YOLO annotations from a label file.
    """
    annotations = []

    if not os.path.exists(label_path):
        return annotations

    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            ann = parse_yolo_label_line(line)

            if ann is None:
                continue

            if DRAW_ONLY_CLASS_IDS is not None:
                if ann["class_id"] not in DRAW_ONLY_CLASS_IDS:
                    continue

            annotations.append(ann)

    return annotations


def get_image_files(images_dir):
    """
    Return sorted image files from YOLO_IMAGES_DIR.
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

print("Loading class names...")
class_names = load_class_names(YOLO_CLASSES_FILE)

if class_names:
    print("Classes found:")
    for class_id, class_name in class_names.items():
        print(f"  {class_id}: {class_name}")
else:
    print("No classes loaded. Labels will show class IDs only.")

print("")

if CLEAR_BB_FOLDER_ON_RUN and os.path.isdir(BB_OUTPUT_DIR):
    print(f"Clearing old BB folder: {BB_OUTPUT_DIR}")
    shutil.rmtree(BB_OUTPUT_DIR)

os.makedirs(BB_OUTPUT_DIR, exist_ok=True)

if not os.path.isdir(YOLO_IMAGES_DIR):
    raise FileNotFoundError(f"Images folder not found: {YOLO_IMAGES_DIR}")

if not os.path.isdir(YOLO_LABELS_DIR):
    raise FileNotFoundError(f"Labels folder not found: {YOLO_LABELS_DIR}")

image_files = get_image_files(YOLO_IMAGES_DIR)

if MAX_IMAGES_TO_DRAW is not None:
    image_files = image_files[:MAX_IMAGES_TO_DRAW]

print(f"Images to process: {len(image_files)}")
print(f"Source images: {YOLO_IMAGES_DIR}")
print(f"Source labels: {YOLO_LABELS_DIR}")
print(f"BB output: {BB_OUTPUT_DIR}")
print("")

processed_images = 0
saved_images = 0
missing_label_files = 0
empty_label_files = 0
boxes_drawn = 0
invalid_images = 0

for image_file_name in tqdm(image_files, desc="Drawing YOLO BBs"):
    image_path = os.path.join(YOLO_IMAGES_DIR, image_file_name)
    label_path = image_to_label_path(image_file_name)

    image = cv2.imread(image_path)

    if image is None:
        invalid_images += 1
        print(f"Warning: could not read image: {image_path}")
        continue

    img_height, img_width = image.shape[:2]

    label_exists = os.path.exists(label_path)

    if not label_exists:
        missing_label_files += 1

        if not SAVE_IMAGES_WITHOUT_LABELS:
            continue

        output_path = os.path.join(BB_OUTPUT_DIR, image_file_name)
        cv2.imwrite(output_path, image)
        saved_images += 1
        processed_images += 1
        continue

    yolo_annotations = read_yolo_labels(label_path)

    if len(yolo_annotations) == 0:
        empty_label_files += 1

        if not SAVE_IMAGES_WITH_EMPTY_LABELS:
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
            thickness=BOX_THICKNESS
        )

        if DRAW_LABELS:
            class_name = class_names.get(class_id, f"class_{class_id}")

            if DRAW_CONFIDENCE_IF_PRESENT and ann["confidence"] is not None:
                label_text = f"{class_id}: {class_name} {ann['confidence']:.2f}"
            else:
                label_text = f"{class_id}: {class_name}"

            draw_text_with_background(
                image=image,
                text=label_text,
                x=x1,
                y=y1,
                color=color
            )

        boxes_drawn += 1

    output_path = os.path.join(BB_OUTPUT_DIR, image_file_name)
    cv2.imwrite(output_path, image)

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
print(f"BB inspection folder: {BB_OUTPUT_DIR}")