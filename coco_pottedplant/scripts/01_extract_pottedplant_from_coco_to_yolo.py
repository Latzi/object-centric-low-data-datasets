import argparse
import os
import json
import shutil
from tqdm import tqdm
from collections import defaultdict


DEFAULT_TARGET_CATEGORY_NAME = "potted plant"
DEFAULT_YOLO_CLASS_ID = 0
DEFAULT_SPLITS = ["train", "val"]


# ============================================================
# ARGUMENTS
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Extract the COCO potted plant category from local COCO 2017 "
            "images and annotations, and write a YOLO-format subset."
        )
    )

    parser.add_argument(
        "--coco-root",
        default=os.environ.get("COCO_ROOT"),
        help=(
            "Path to the local COCO dataset root. The expected structure is: "
            "COCO_ROOT/train2017, COCO_ROOT/val2017, and "
            "COCO_ROOT/annotations_trainval2017/annotations. "
            "You can also set the COCO_ROOT environment variable."
        ),
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Output directory for the YOLO-format potted plant subset. "
            "Default: COCO_ROOT/YOLO_pottedplant."
        ),
    )

    parser.add_argument(
        "--splits",
        nargs="+",
        default=DEFAULT_SPLITS,
        choices=["train", "val"],
        help="COCO splits to process. Default: train val.",
    )

    parser.add_argument(
        "--target-category-name",
        default=DEFAULT_TARGET_CATEGORY_NAME,
        help="COCO category name to extract. Default: potted plant.",
    )

    parser.add_argument(
        "--yolo-class-id",
        type=int,
        default=DEFAULT_YOLO_CLASS_ID,
        help="YOLO class ID to write for the selected category. Default: 0.",
    )

    return parser.parse_args()


# ============================================================
# VALIDATION
# ============================================================

def validate_inputs(coco_root, ann_dir, splits):
    if coco_root is None or str(coco_root).strip() == "":
        raise RuntimeError(
            "COCO root was not provided. Pass --coco-root or set the COCO_ROOT "
            "environment variable."
        )

    if not os.path.isdir(coco_root):
        raise FileNotFoundError(
            f"COCO root does not exist: {coco_root}"
        )

    if not os.path.isdir(ann_dir):
        raise FileNotFoundError(
            f"COCO annotations directory does not exist: {ann_dir}"
        )

    for split in splits:
        img_dir = os.path.join(coco_root, f"{split}2017")
        ann_path = os.path.join(ann_dir, f"instances_{split}2017.json")

        if not os.path.isdir(img_dir):
            raise FileNotFoundError(
                f"COCO image directory for split '{split}' does not exist: {img_dir}"
            )

        if not os.path.isfile(ann_path):
            raise FileNotFoundError(
                f"COCO annotation file for split '{split}' does not exist: {ann_path}"
            )


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

def main():
    args = parse_args()

    coco_dir = os.path.abspath(args.coco_root)
    ann_dir = os.path.join(coco_dir, "annotations_trainval2017", "annotations")

    if args.output_dir is None:
        out_dir = os.path.join(coco_dir, "YOLO_pottedplant")
    else:
        out_dir = os.path.abspath(args.output_dir)

    splits = args.splits
    target_category_name = args.target_category_name
    yolo_class_id = args.yolo_class_id

    validate_inputs(coco_dir, ann_dir, splits)

    print("COCO potted plant extraction")
    print("============================")
    print(f"COCO root:        {coco_dir}")
    print(f"Annotation dir:   {ann_dir}")
    print(f"Output dir:       {out_dir}")
    print(f"Splits:           {splits}")
    print(f"Target category:  {target_category_name}")
    print(f"YOLO class ID:    {yolo_class_id}")

    overall_summary = {}

    os.makedirs(out_dir, exist_ok=True)

    for split in splits:
        print(f"\nProcessing {split}...")

        img_dir = os.path.join(coco_dir, f"{split}2017")
        ann_path = os.path.join(ann_dir, f"instances_{split}2017.json")
        out_img_dir = os.path.join(out_dir, "images", split)
        out_lbl_dir = os.path.join(out_dir, "labels", split)

        os.makedirs(out_img_dir, exist_ok=True)
        os.makedirs(out_lbl_dir, exist_ok=True)

        with open(ann_path, "r", encoding="utf-8") as f:
            coco = json.load(f)

        target_cat_ids = find_target_category_ids(
            coco["categories"],
            target_category_name,
        )

        if not target_cat_ids:
            raise RuntimeError(
                f"Could not find target category '{target_category_name}' in {ann_path}"
            )

        print(f"Target category name: {target_category_name}")
        print(f"Matching COCO category IDs: {target_cat_ids}")

        # Map image_id -> image info
        id2img = {img["id"]: img for img in coco["images"]}

        # Map image_id -> all target-category annotations
        imgid2anns = defaultdict(list)
        for ann in coco["annotations"]:
            if ann["category_id"] in target_cat_ids and not ann.get("iscrowd", 0):
                imgid2anns[ann["image_id"]].append(ann)

        image_ids = sorted(imgid2anns.keys())
        print(
            f"Found {len(image_ids)} images with at least one "
            f"'{target_category_name}' instance."
        )

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

            label_path = os.path.join(
                out_lbl_dir,
                os.path.splitext(fname)[0] + ".txt",
            )

            yolo_lines = []

            for ann in imgid2anns[img_id]:
                x, y, bw, bh = ann["bbox"]  # COCO bbox: x_min, y_min, width, height

                x_center = (x + bw / 2.0) / w
                y_center = (y + bh / 2.0) / h
                bw_norm = bw / w
                bh_norm = bh / h

                yolo_lines.append(
                    f"{yolo_class_id} "
                    f"{x_center:.6f} {y_center:.6f} "
                    f"{bw_norm:.6f} {bh_norm:.6f}"
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

        print(f"{copied} images with '{target_category_name}' processed for {split}.")
        print(f"{total_boxes} YOLO boxes written for {split}.")

    write_classes_file(out_dir)
    write_data_yaml(out_dir)

    summary_path = os.path.join(out_dir, "conversion_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(overall_summary, f, indent=2)

    print("\nALL DONE.")
    print(f"YOLO subset written to: {out_dir}")
    print(f"classes.txt written to: {os.path.join(out_dir, 'classes.txt')}")
    print(f"data.yaml written to: {os.path.join(out_dir, 'data.yaml')}")
    print(f"summary written to: {summary_path}")


if __name__ == "__main__":
    main()