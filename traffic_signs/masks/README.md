# TrafficSigns Masks

This folder documents mask handling for the **TrafficSigns** subset.

## Purpose

Explicit binary mask image files are not stored separately in this repository.

Instead, bounding-box masks can be generated from the released YOLO-format bounding boxes when required by bounding-box-guided generative models.

## How to generate masks

For a `256x256` TrafficSigns image, a bounding-box mask can be rasterized from the YOLO annotation.

A simple mask has:

    1 inside the bounding box
    0 outside the bounding box

If an image has multiple bounding boxes, the mask can include all boxes.

## Source annotations

The canonical released annotations for TrafficSigns are the YOLO label files stored under:

    ../Train_Data/labels/train/
    ../Train_Data/labels/val/
    ../Train_Data/test/labels/

## Related files

    ../annotations/README.md
    ../metadata/traffic_signs_manifest.csv
    ../metadata/traffic_signs_summary.json
    ../data.yaml

## Notes

This folder does not contain mask image files.

It documents how masks can be derived from the released bounding-box annotations.
