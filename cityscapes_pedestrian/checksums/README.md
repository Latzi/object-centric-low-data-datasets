# Cityscapes--Pedestrian Checksums



This folder documents checksum usage for the **Cityscapes--Pedestrian** subset.



## Purpose



Because this subset is released in **abstract / non-image form**, checksum files in this folder are intended to verify the integrity of released non-image artifacts.



These may include:



- manifest files

- metadata files

- split files

- annotation tables

- reconstruction / preparation scripts



## What checksum files may cover



Checksum files in this folder may be used to verify:



- `../manifests/`

- `../metadata/`

- `../splits/`

- `../annotations/`

- `../reconstruct_cityscapes.py`



## What is NOT covered here



This folder is not intended to provide checksums for:



- original Cityscapes images

- cropped pedestrian image patches

- preview images or thumbnails



Those image files are not redistributed in this repository.



## Notes



If checksum files are added later, this folder should make clear:



- which released files are covered

- which checksum algorithm is used

- which checksum file is the canonical public integrity record

