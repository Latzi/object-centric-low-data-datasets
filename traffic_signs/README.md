# Traffic Signs

This folder contains the **Traffic Signs** subset of the **Object-Centric Low-Data Datasets** collection.

## Summary

Traffic Signs is the directly released subset in this repository. It consists of object-centric `256×256` crops derived from `1024×768` street-view images. The original categories **Traffic Sign** and **Damaged Traffic Sign** are merged into a single target class: `traffic_sign`.

Bounding boxes were obtained using a YOLOv5x detector, and each crop was generated with randomized centering so that the object is not always placed in exactly the same position within the crop. In the FDGAN low-data setup, this subset contains fewer than 3k images.

## Why this subset matters

Compared with the other subsets in the collection, Traffic Signs provides the simplest visual regime:

- mostly single-object images
- little or no occlusion
- sharp object boundaries
- high contrast
- relatively low background clutter

This makes the subset useful for studying fine object detail, edge fidelity, and low-data object-centric generation in a cleaner setting than dense pedestrian scenes.

## Contents

This folder is intended to contain:

- `images/` — released crop images
- `annotations/` — bounding-box labels and class mapping
- `masks/` — aligned binary masks
- `splits/` — train / validation / test split files
- `metadata/` — manifest and dataset summary files
- `checksums/` — file integrity checks

## Class definition

This subset uses a single merged class:

- `0` → `traffic_sign`

## Data format

- crop size: `256×256`
- target type: object-centric crop
- class count: `1`
- annotation type: bounding boxes
- release mode: direct release

## Split files

The split definitions for this subset are stored in:

- `splits/train.txt`
- `splits/val.txt`
- `splits/test.txt`

## Metadata

Canonical subset metadata is stored in:

- `metadata/traffic_signs_manifest.csv`
- `metadata/traffic_signs_summary.json`

## Notes

This subset is directly released because it is author-created and does not inherit the redistribution constraints of the Cityscapes- and COCO-derived subsets.
