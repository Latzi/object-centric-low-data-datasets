# TrafficSigns Train_Data

This folder contains the released YOLO-style split structure for the **TrafficSigns** subset.

## Purpose

This is the training-ready dataset folder for the direct-release TrafficSigns subset.

Unlike the Cityscapes--Pedestrian and COCO PottedPlant subsets, TrafficSigns is released directly with image files and YOLO-format label files.

## Layout

    Train_Data/
        images/
            train/
            val/
        labels/
            train/
            val/
        test/
            images/
            labels/

## Split counts

| Split | Count |
|---|---:|
| train | 2256 |
| val | 451 |
| test | 302 |
| total | 3009 |

## Class mapping

    0 -> TrafficSigns

## Notes

Each image should have a corresponding YOLO label file with the same base filename and the `.txt` extension.

The canonical TrafficSigns metadata files are stored in:

    ../metadata/traffic_signs_manifest.csv
    ../metadata/traffic_signs_summary.json

The YOLO configuration file is stored in:

    ../data.yaml
