import os
import cv2
import shutil
from tqdm import tqdm


# ============================================================
# PATH SETUP
# ============================================================

COCO_DIR = r"C:\Users\richm\Downloads\COCO_Dataset"

# Output of step 02
SOURCE_DIR = os.path.join(COCO_DIR, "YOLO_pottedplant_cropped")
IMAGES_ROOT = os.path.join(SOURCE_DIR, "images")
LABELS_ROOT = os.path.join(SOURCE_DIR, "labels")
CLASSES_FILE = os.path.join(SOURCE_DIR, "classes.txt")

# Debug output
BB_ROOT = os.path.join(SOURCE_DIR, "BB")

SPLITS = ["train", "val"]


# ============================================================
# DRAWING SETTINGS
# ============================================================

CLEAR_BB_FOLDER_ON_RUN = True
DRAW_LABELS = True
DRAW_CONFIDENCE_IF_PRESENT = False   # labels are standard YOLO, so usually False
BOX_THICKNESS = 2
TEXT_SCALE = 0.45
TEXT_THICKNESS = 1

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

SAVE_IMAGES_WITHOUT_LABELS = True
SAVE_IMAGES_WITH_EMPTY_LABELS = True

# Use None to draw all classes
DRAW_ONLY_CLASS_IDS = None

# Use None to draw all images
MAX_IMAGES_TO_DRAW = None


# ============================================================
# HELPERS
# ============================================================

def load_class_names(classes_file):
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


def read_yolo_labels(label_path):
    annotations = []

    if not os.path.exists(label_path):
        return annotations

    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            ann = parse_yolo_label_line(line)
            if ann is None:
                continue

            if DRAW_ONLY_CLASS_IDS is not None and ann["class_id"] not in DRAW_ONLY_CLASS_IDS:
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


def draw_text_with_background(image, text, x, y, color):
    font = cv2.FONT_HERSHEY_SIMPLEX

    text_size, baseline = cv2.getTextSize(
        text,
        font,
        TEXT_SCALE,
        TEXT_THICKNESS
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

print("Loading class names...")
class_names = load_class_names(CLASSES_FILE)

if class_names:
    print("Classes found:")
    for class_id, class_name in class_names.items():
        print(f"  {class_id}: {class_name}")
else:
    print("No classes loaded. Labels will show class IDs only.")

if CLEAR_BB_FOLDER_ON_RUN and os.path.isdir(BB_ROOT):
    print(f"Clearing old BB folder: {BB_ROOT}")
    shutil.rmtree(BB_ROOT)

os.makedirs(BB_ROOT, exist_ok=True)

for split in SPLITS:
    print(f"\nProcessing split: {split}")

    images_dir = os.path.join(IMAGES_ROOT, split)
    labels_dir = os.path.join(LABELS_ROOT, split)
    bb_out_dir = os.path.join(BB_ROOT, split)

    if not os.path.isdir(images_dir):
        print(f"Skipping missing images folder: {images_dir}")
        continue

    if not os.path.isdir(labels_dir):
        print(f"Skipping missing labels folder: {labels_dir}")
        continue

    os.makedirs(bb_out_dir, exist_ok=True)

    image_files = get_image_files(images_dir)
    if MAX_IMAGES_TO_DRAW is not None:
        image_files = image_files[:MAX_IMAGES_TO_DRAW]

    processed_images = 0
    saved_images = 0
    missing_label_files = 0
    empty_label_files = 0
    boxes_drawn = 0
    invalid_images = 0

    for image_file_name in tqdm(image_files, desc=f"Drawing YOLO BBs ({split})"):
        image_path = os.path.join(images_dir, image_file_name)
        label_path = os.path.join(labels_dir, os.path.splitext(image_file_name)[0] + ".txt")

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

            output_path = os.path.join(bb_out_dir, image_file_name)
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

        output_path = os.path.join(bb_out_dir, image_file_name)
        cv2.imwrite(output_path, image)

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