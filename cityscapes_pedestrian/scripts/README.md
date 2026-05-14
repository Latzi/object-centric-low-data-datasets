\# Cityscapes--Pedestrian Scripts



This folder contains the reconstruction / preparation pipeline used for the \*\*Cityscapes--Pedestrian\*\* subset.



\## Pipeline order



The scripts in this folder are intended to be used in the following order:



1\. `01\_create\_crops\_from\_cityscapes\_with\_bb.py`

2\. `02\_filter\_cropped\_images.py`

3\. `03\_create\_yolo\_annotations\_from\_filtered.py`

4\. `04\_draw\_yolo\_bb\_debug.py`



\## Stage summary



\### 01 — Create crops from original Cityscapes sources

This stage starts from the authorized upstream Cityscapes data and related annotation sources, merges relevant person-related categories, removes likely duplicate cross-source objects, generates candidate `256×256` crops, and exports an intermediate cropped dataset plus COCO-style annotations.



\### 02 — Filter cropped images

This stage applies subset-selection logic to the cropped intermediate dataset. It supports filtering by object counts and overlap statistics, allowing the user to control difficulty and final subset composition.



\### 03 — Convert filtered subset to YOLO format

This stage converts the filtered subset into YOLO-compatible images, labels, class definitions, and dataset configuration files.



\### 04 — Draw YOLO bounding boxes for inspection

This stage is a debug / inspection utility that renders YOLO bounding boxes on images for visual verification.



\## Notes



These scripts are part of the reconstruction / preparation layer for the Cityscapes-derived subset.



This repository does not redistribute Cityscapes image data or cropped Cityscapes pedestrian patches.

Users must separately obtain access to the original Cityscapes dataset and comply with the upstream terms.



See also:



\- `../README.md`

\- `../manifests/`

\- `../metadata/`

\- `../../LICENSES/cityscapes\_notice.txt`

