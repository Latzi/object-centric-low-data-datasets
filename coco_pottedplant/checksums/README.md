# COCO PottedPlant Checksums



This folder documents checksum usage for the **COCO PottedPlant** subset.



## Purpose



Because this subset is released in **metadata / reconstruction-first form**, checksum files in this folder are intended to verify the integrity of released non-image artifacts.



These may include:



- manifest files

- metadata files

- split files

- annotation documentation

- reconstruction / preparation scripts

- pipeline configuration files



## What checksum files may cover



Checksum files in this folder may be used to verify:



- `../README.md`

- `../manifests/`

- `../metadata/`

- `../splits/`

- `../annotations/`

- `../reconstruct_coco.py`

- `../scripts/`



## What is NOT covered here



This folder is not intended to provide checksums for:



- original MS-COCO image files

- blanket packaged cropped image subsets

- preview images or thumbnails



Those image files are not the primary public release artifacts for this subset.



## Notes



If checksum files are added later, this folder should make clear:



- which released files are covered

- which checksum algorithm is used

- which checksum file is the canonical public integrity record

