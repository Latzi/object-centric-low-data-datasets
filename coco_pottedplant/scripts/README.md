# COCO PottedPlant Scripts



This folder contains the reconstruction / preparation pipeline used for the **COCO PottedPlant** subset.



## Pipeline order



The scripts in this folder are intended to be used in the following order:



1. `01_extract_pottedplant_from_coco_to_yolo.py`

2. `02_create_instance_crops_from_yolo_pottedplant.py`

3. `03_draw_cropped_yolo_bb_debug.py`



## Stage summary



### 01 — Extract potted plant from COCO into YOLO full-image format

This stage starts from the official downloadable COCO images and annotations, selects the target category, and writes a YOLO-compatible subset while preserving the original COCO split structure.



### 02 — Create 256x256 per-instance crops

This stage converts the extracted full-image YOLO subset into an object-centric cropped subset. One crop is generated per selected instance, using random offset / margin so that the object is not always centered. Small boxes can be skipped, and intersecting potted-plant boxes may also be kept in the cropped labels.



### 03 — Draw YOLO bounding boxes for inspection

This stage is a debug / inspection utility that renders YOLO bounding boxes on the cropped images for visual verification.



## Notes



These scripts are part of the reconstruction / preparation layer for the COCO-derived subset.



This repository does not assume blanket redistribution rights for all COCO-derived image files. Users must obtain the upstream COCO data separately and comply with the original terms that apply to those files.



See also:



- `../README.md`

- `../manifests/`

- `../metadata/`

- `../../LICENSES/coco_notice.txt`

