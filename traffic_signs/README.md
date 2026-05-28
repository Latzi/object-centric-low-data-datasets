# TrafficSigns

This folder contains the **TrafficSigns** subset of the **Object-Centric Low-Data Datasets** collection.

## Summary

TrafficSigns is the directly released subset in this repository. It consists of final released `256Ã—256` object-centric crop images derived from larger street-view frames. The original sign-related categories are merged into a single target class used throughout this subset.

The subset is organized in a YOLO-compatible structure so that it can be used directly for model training and evaluation.

## Why this subset matters

Compared with the other subsets in the collection, TrafficSigns provides the simplest visual regime:

- mostly single-object images
- little or no occlusion
- sharp object boundaries
- high contrast
- relatively low background clutter

This makes the subset useful for studying fine object detail, edge fidelity, and low-data object-centric generation in a cleaner setting than dense pedestrian scenes.

## Canonical dataset layout

The canonical released layout for this subset is:

- `Train_Data/images/train/`
- `Train_Data/images/val/`
- `Train_Data/test/images/`

with matching YOLO label files in:

- `Train_Data/labels/train/`
- `Train_Data/labels/val/`
- `Train_Data/test/labels/`

The YOLO dataset configuration file is:

- `data.yaml`

## Metadata and documentation

Canonical metadata for this subset is stored in:

- `metadata/traffic_signs_manifest.csv`
- `metadata/traffic_signs_summary.json`

Additional annotation and split documentation is provided in:

- `annotations/README.md`
- `splits/README.md`

## Class definition

This subset uses a single merged class:

- `0` â†’ `TrafficSigns`

The class file is stored in:

- `annotations/classes.txt`

## Release mode

TrafficSigns is the **direct-release** subset in this collection. Unlike the Cityscapes- and COCO-derived subsets, it does not inherit the same redistribution constraints and can therefore be released here as final dataset files together with metadata and support files.

## Notes

The `Train_Data/` directory is the authoritative source for released images and labels in this subset. Metadata files should remain consistent with the files stored there.

## Annotation provenance

Candidate bounding boxes for the TrafficSigns subset were generated using YOLOv5x for traffic-sign-related categories and manually reviewed before release.

The released YOLO labels should be interpreted as a reviewed annotation layer rather than raw detector output.
