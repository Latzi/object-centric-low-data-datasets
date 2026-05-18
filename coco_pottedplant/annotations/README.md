\# COCO PottedPlant Annotations



This folder documents the annotation layer for the \*\*COCO PottedPlant\*\* subset.



\## Purpose



Because this subset is released in \*\*metadata / reconstruction-first form\*\*, the annotation layer in this repository is primarily documentation and metadata support rather than a blanket packaged release of upstream-derived image annotations.



\## Annotation flow in the reconstruction pipeline



The current COCO pipeline has two annotation-producing stages:



\### Step 01 — Full-image YOLO subset

`01\_extract\_pottedplant\_from\_coco\_to\_yolo.py` reads the official COCO images and annotations, selects the target category, and writes a YOLO-format full-image subset that preserves the original COCO split structure (`train` and `val`).



\### Step 02 — Cropped YOLO subset

`02\_create\_instance\_crops\_from\_yolo\_pottedplant.py` creates `256×256` per-instance crops from the Step 01 subset and writes cropped YOLO labels for those crops.



\## Class mapping



The public standardized merged class name for this subset is:



\- `0` → `potted\_plant`



\## Local annotation outputs



In a local authorized workflow, the annotation files are expected to be produced in the following locations:



\### Step 01 output

\- `YOLO\_pottedplant/labels/train/`

\- `YOLO\_pottedplant/labels/val/`



\### Step 02 output

\- `YOLO\_pottedplant\_cropped/labels/train/`

\- `YOLO\_pottedplant\_cropped/labels/val/`



\## YOLO annotation format



Annotations use standard YOLO bounding-box format.



Each line in a label file has the form:



`class\_id x\_center y\_center width height`



where coordinates are normalized to the image size and lie in `\[0, 1]`.



\## Notes



\- The current crop-generation configuration keeps all intersecting potted-plant boxes in the cropped labels.

\- The public manifest in `../manifests/coco\_pottedplant\_manifest.csv` should remain consistent with the annotation logic used by the local reconstruction pipeline.

\- This repository does not assume blanket redistribution rights for all upstream-derived image annotation/image bundles.



See also:



\- `../scripts/README.md`

\- `../metadata/pipeline\_config\_coco.json`

\- `../splits/README.md`

\- `../../LICENSES/coco\_notice.txt`

