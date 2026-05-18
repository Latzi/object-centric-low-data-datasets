import os
import json
import shutil
from tqdm import tqdm
from collections import defaultdict


# ============================================================
# PATH SETUP
# ============================================================

COCO_DIR = r"C:\Users\richm\Downloads\COCO_Dataset"
ANN_DIR = os.path.join(COCO_DIR, "annotations_trainval2017", "annotations")
OUT_DIR = os.path.join(COCO_DIR, "YOLO_pottedplant")

SPLITS = ["train", "val"]

TARGET_CATEGORY_NAME = "potted plant"
YOLO_CLASS_ID = 0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_target_category_ids(categories, target_name):
    """
    Find all category IDs in the COCO categories list whose name matches
    the requested target category.
    """
    target_ids = []
    for cat in categories:
        name = str(cat.get("name", "")).strip().lower()
        if name == target_name.strip().lower():
            target_ids.append(cat["id"])
    return target_ids


def write_classes_file(out_dir):
    classes_path = os.path.join(out_dir, "classes.txt")
    with open(classes_path, "w", encoding="utf-8") as f:
        f.write("potted_plant\n")


def write_data_yaml(out_dir):
    yaml_path = os.path.join(out_dir, "data.yaml")
    yolo_path = out_dir.replace("\\", "/")

    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(f"path: {yolo_path}\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n")
        f.write("\n")
        f.write("names:\n")
        f.write("  0: potted_plant\n")


# ============================================================
# MAIN SCRIPT
# ============================================================

overall_summary = {}

os.makedirs(OUT_DIR, exist_ok=True)

for split in SPLITS:
    print(f"\nProcessing {split}...")

    img_dir = os.path.join(COCO_DIR, f"{split}2017")
    ann_path = os.path.join(ANN_DIR, f"instances_{split}2017.json")
    out_img_dir = os.path.join(OUT_DIR, "images", split)
    out_lbl_dir = os.path.join(OUT_DIR, "labels", split)

    os.makedirs(out_img_dir, exist_ok=True)
    os.makedirs(out_lbl_dir, exist_ok=True)

    with open(ann_path, "r", encoding="utf-8") as f:
        coco = json.load(f)

    target_cat_ids = find_target_category_ids(coco["categories"], TARGET_CATEGORY_NAME)

    if not target_cat_ids:
        raise RuntimeError(
            f"Could not find target category '{TARGET_CATEGORY_NAME}' in {ann_path}"
        )

    print(f"Target category name: {TARGET_CATEGORY_NAME}")
    print(f"Matching COCO category IDs: {target_cat_ids}")

    # Map image_id -> image info
    id2img = {img["id"]: img for img in coco["images"]}

    # Map image_id -> all target-category annotations
    imgid2anns = defaultdict(list)
    for ann in coco["annotations"]:
        if ann["category_id"] in target_cat_ids and not ann.get("iscrowd", 0):
            imgid2anns[ann["image_id"]].append(ann)

    image_ids = set(imgid2anns.keys())
    print(f"Found {len(image_ids)} images with at least one '{TARGET_CATEGORY_NAME}' instance.")

    copied = 0
    total_boxes = 0
    missing_images = 0

    for img_id in tqdm(image_ids, desc=f"Copying/labeling {split}"):
        imginfo = id2img[img_id]
        fname = imginfo["file_name"]
        w, h = imginfo["width"], imginfo["height"]

        src_img_path = os.path.join(img_dir, fname)
        tgt_img_path = os.path.join(out_img_dir, fname)

        if not os.path.exists(src_img_path):
            print(f"Image missing: {src_img_path}")
            missing_images += 1
            continue

        shutil.copy2(src_img_path, tgt_img_path)

        label_path = os.path.join(out_lbl_dir, os.path.splitext(fname)[0] + ".txt")
        yolo_lines = []

        for ann in imgid2anns[img_id]:
            x, y, bw, bh = ann["bbox"]  # COCO bbox: x_min, y_min, width, height

            x_center = (x + bw / 2.0) / w
            y_center = (y + bh / 2.0) / h
            bw_norm = bw / w
            bh_norm = bh / h

            yolo_lines.append(
                f"{YOLO_CLASS_ID} {x_center:.6f} {y_center:.6f} {bw_norm:.6f} {bh_norm:.6f}"
            )

        with open(label_path, "w", encoding="utf-8") as f:
            f.write("\n".join(yolo_lines))

        total_boxes += len(yolo_lines)
        copied += 1

    overall_summary[split] = {
        "images_with_target_class": copied,
        "boxes_written": total_boxes,
        "missing_images": missing_images,
    }

    print(f"{copied} images with '{TARGET_CATEGORY_NAME}' processed for {split}.")
    print(f"{total_boxes} YOLO boxes written for {split}.")

write_classes_file(OUT_DIR)
write_data_yaml(OUT_DIR)

summary_path = os.path.join(OUT_DIR, "conversion_summary.json")
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(overall_summary, f, indent=2)

print("\nALL DONE.")
print(f"YOLO subset written to: {OUT_DIR}")
print(f"classes.txt written to: {os.path.join(OUT_DIR, 'classes.txt')}")
print(f"data.yaml written to: {os.path.join(OUT_DIR, 'data.yaml')}")
print(f"summary written to: {summary_path}")