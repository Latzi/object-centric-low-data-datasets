import os
import json
import shutil
import random
from pathlib import Path

import cv2
from tqdm import tqdm


# ============================================================
# PATH SETUP
# ============================================================

COCO_DIR = r"C:\Users\richm\Downloads\COCO_Dataset"

# Output of step 01
SOURCE_DIR = os.path.join(COCO_DIR, "YOLO_pottedplant")
SOURCE_IMAGES_ROOT = os.path.join(SOURCE_DIR, "images")
SOURCE_LABELS_ROOT = os.path.join(SOURCE_DIR, "labels")

# Output of this cropping step
OUT_DIR = os.path.join(COCO_DIR, "YOLO_pottedplant_cropped")
OUT_IMAGES_ROOT = os.path.join(OUT_DIR, "images")
OUT_LABELS_ROOT = os.path.join(OUT_DIR, "labels")
OUT_CLASSES_FILE = os.path.join(OUT_DIR, "classes.txt")
OUT_DATA_YAML = os.path.join(OUT_DIR, "data.yaml")
OUT_SUMMARY_JSON = os.path.join(OUT_DIR, "crop_summary.json")

SPLITS = ["train", "val"]

# ============================================================
# CROP SETTINGS
# ============================================================

CROP_SIZE = 256
RANDOM_SEED = 42
CLEAR_OUTPUT_ON_RUN = True

# Skip very small boxes that would make the crop/object relationship too weak
MIN_BOX_WIDTH_PIXELS = 12
MIN_BOX_HEIGHT_PIXELS = 12

# By default we keep only the selected instance in each crop label.
# If you want all intersecting potted-plant boxes kept in the crop,
# set this to True.
INCLUDE_ALL_INTERSECTING_BOXES = True

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

YOLO_CLASS_NAME = "potted_plant"
YOLO_CLASS_ID = 0


# ============================================================
# HELPERS
# ============================================================

def parse_yolo_label_file(label_path):
    anns = []

    if not os.path.exists(label_path):
        return anns

    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            class_id = int(float(parts[0]))
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])

            anns.append({
                "class_id": class_id,
                "x_center": x_center,
                "y_center": y_center,
                "width": width,
                "height": height,
            })

    return anns


def yolo_to_pixel_bbox(ann, img_w, img_h):
    x_center = ann["x_center"] * img_w
    y_center = ann["y_center"] * img_h
    bw = ann["width"] * img_w
    bh = ann["height"] * img_h

    x1 = x_center - bw / 2.0
    y1 = y_center - bh / 2.0
    x2 = x_center + bw / 2.0
    y2 = y_center + bh / 2.0

    return x1, y1, x2, y2


def pixel_bbox_to_yolo(x1, y1, x2, y2, img_w, img_h):
    bw = x2 - x1
    bh = y2 - y1
    x_center = x1 + bw / 2.0
    y_center = y1 + bh / 2.0

    return (
        x_center / img_w,
        y_center / img_h,
        bw / img_w,
        bh / img_h,
    )


def clip_bbox_to_crop(box, crop_x, crop_y, crop_size):
    x1, y1, x2, y2 = box

    inter_left = max(x1, crop_x)
    inter_top = max(y1, crop_y)
    inter_right = min(x2, crop_x + crop_size)
    inter_bottom = min(y2, crop_y + crop_size)

    if inter_right <= inter_left or inter_bottom <= inter_top:
        return None

    # shift into crop coordinates
    cx1 = inter_left - crop_x
    cy1 = inter_top - crop_y
    cx2 = inter_right - crop_x
    cy2 = inter_bottom - crop_y

    return cx1, cy1, cx2, cy2


def choose_crop_for_box(box, img_w, img_h, rng):
    """
    Choose a 256x256 crop so the selected bbox lies fully inside the crop,
    with random offset when possible.
    """
    x1, y1, x2, y2 = box

    if img_w < CROP_SIZE or img_h < CROP_SIZE:
        return None

    bw = x2 - x1
    bh = y2 - y1

    if bw < MIN_BOX_WIDTH_PIXELS or bh < MIN_BOX_HEIGHT_PIXELS:
        return None

    crop_x_min = max(0, int(x2 - CROP_SIZE))
    crop_x_max = min(int(x1), img_w - CROP_SIZE)

    crop_y_min = max(0, int(y2 - CROP_SIZE))
    crop_y_max = min(int(y1), img_h - CROP_SIZE)

    if crop_x_min > crop_x_max or crop_y_min > crop_y_max:
        return None

    crop_x = rng.randint(crop_x_min, crop_x_max)
    crop_y = rng.randint(crop_y_min, crop_y_max)

    return crop_x, crop_y


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_classes_file():
    with open(OUT_CLASSES_FILE, "w", encoding="utf-8") as f:
        f.write(f"{YOLO_CLASS_NAME}\n")


def write_data_yaml():
    yolo_path = OUT_DIR.replace("\\", "/")
    with open(OUT_DATA_YAML, "w", encoding="utf-8") as f:
        f.write(f"path: {yolo_path}\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n")
        f.write("\n")
        f.write("names:\n")
        f.write(f"  0: {YOLO_CLASS_NAME}\n")


# ============================================================
# MAIN
# ============================================================

if CLEAR_OUTPUT_ON_RUN and os.path.isdir(OUT_DIR):
    shutil.rmtree(OUT_DIR)

ensure_dir(OUT_IMAGES_ROOT)
ensure_dir(OUT_LABELS_ROOT)

rng = random.Random(RANDOM_SEED)

summary = {
    "source_dir": SOURCE_DIR,
    "output_dir": OUT_DIR,
    "crop_size": CROP_SIZE,
    "min_box_width_pixels": MIN_BOX_WIDTH_PIXELS,
    "min_box_height_pixels": MIN_BOX_HEIGHT_PIXELS,
    "include_all_intersecting_boxes": INCLUDE_ALL_INTERSECTING_BOXES,
    "splits": {}
}

for split in SPLITS:
    print(f"\nProcessing split: {split}")

    src_img_dir = os.path.join(SOURCE_IMAGES_ROOT, split)
    src_lbl_dir = os.path.join(SOURCE_LABELS_ROOT, split)

    out_img_dir = os.path.join(OUT_IMAGES_ROOT, split)
    out_lbl_dir = os.path.join(OUT_LABELS_ROOT, split)

    ensure_dir(out_img_dir)
    ensure_dir(out_lbl_dir)

    image_files = sorted([
        f for f in os.listdir(src_img_dir)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    ])

    images_seen = 0
    instance_boxes_seen = 0
    crops_written = 0
    skipped_small_boxes = 0
    skipped_small_images = 0

    for image_name in tqdm(image_files, desc=f"Cropping {split}"):
        img_path = os.path.join(src_img_dir, image_name)
        lbl_path = os.path.join(src_lbl_dir, os.path.splitext(image_name)[0] + ".txt")

        img = cv2.imread(img_path)
        if img is None:
            continue

        img_h, img_w = img.shape[:2]
        images_seen += 1

        anns = parse_yolo_label_file(lbl_path)

        if img_w < CROP_SIZE or img_h < CROP_SIZE:
            skipped_small_images += 1
            continue

        for ann_idx, ann in enumerate(anns):
            if ann["class_id"] != YOLO_CLASS_ID:
                continue

            box = yolo_to_pixel_bbox(ann, img_w, img_h)
            instance_boxes_seen += 1

            bw = box[2] - box[0]
            bh = box[3] - box[1]

            if bw < MIN_BOX_WIDTH_PIXELS or bh < MIN_BOX_HEIGHT_PIXELS:
                skipped_small_boxes += 1
                continue

            crop_origin = choose_crop_for_box(box, img_w, img_h, rng)
            if crop_origin is None:
                skipped_small_boxes += 1
                continue

            crop_x, crop_y = crop_origin
            crop_img = img[crop_y:crop_y + CROP_SIZE, crop_x:crop_x + CROP_SIZE]

            if crop_img.shape[0] != CROP_SIZE or crop_img.shape[1] != CROP_SIZE:
                continue

            crop_name = f"{Path(image_name).stem}_inst{ann_idx:04d}_crop_{crop_x}_{crop_y}.jpg"
            crop_img_path = os.path.join(out_img_dir, crop_name)
            crop_lbl_path = os.path.join(out_lbl_dir, Path(crop_name).stem + ".txt")

            crop_lines = []

            if INCLUDE_ALL_INTERSECTING_BOXES:
                for other_ann in anns:
                    if other_ann["class_id"] != YOLO_CLASS_ID:
                        continue

                    other_box = yolo_to_pixel_bbox(other_ann, img_w, img_h)
                    clipped = clip_bbox_to_crop(other_box, crop_x, crop_y, CROP_SIZE)
                    if clipped is None:
                        continue

                    cx1, cy1, cx2, cy2 = clipped
                    xcn, ycn, wn, hn = pixel_bbox_to_yolo(cx1, cy1, cx2, cy2, CROP_SIZE, CROP_SIZE)
                    crop_lines.append(
                        f"{YOLO_CLASS_ID} {xcn:.6f} {ycn:.6f} {wn:.6f} {hn:.6f}"
                    )
            else:
                clipped = clip_bbox_to_crop(box, crop_x, crop_y, CROP_SIZE)
                if clipped is None:
                    continue

                cx1, cy1, cx2, cy2 = clipped
                xcn, ycn, wn, hn = pixel_bbox_to_yolo(cx1, cy1, cx2, cy2, CROP_SIZE, CROP_SIZE)
                crop_lines.append(
                    f"{YOLO_CLASS_ID} {xcn:.6f} {ycn:.6f} {wn:.6f} {hn:.6f}"
                )

            cv2.imwrite(crop_img_path, crop_img)
            with open(crop_lbl_path, "w", encoding="utf-8") as f:
                f.write("\n".join(crop_lines))

            crops_written += 1

    summary["splits"][split] = {
        "images_seen": images_seen,
        "instance_boxes_seen": instance_boxes_seen,
        "crops_written": crops_written,
        "skipped_small_boxes": skipped_small_boxes,
        "skipped_small_images": skipped_small_images,
    }

    print(f"Split {split}:")
    print(f"  images_seen: {images_seen}")
    print(f"  instance_boxes_seen: {instance_boxes_seen}")
    print(f"  crops_written: {crops_written}")
    print(f"  skipped_small_boxes: {skipped_small_boxes}")
    print(f"  skipped_small_images: {skipped_small_images}")

write_classes_file()
write_data_yaml()

with open(OUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\nALL DONE.")
print(f"Cropped YOLO subset written to: {OUT_DIR}")
print(f"classes.txt written to: {OUT_CLASSES_FILE}")
print(f"data.yaml written to: {OUT_DATA_YAML}")
print(f"summary written to: {OUT_SUMMARY_JSON}")