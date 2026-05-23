# TrafficSigns Train and Validation Images

This folder contains released TrafficSigns image files for the training and validation splits.

## Layout

    images/
        train/
        val/

## Matching labels

Matching YOLO label files are stored under:

    ../labels/train/
    ../labels/val/

Each image should have a corresponding label file with the same base filename.

For example:

    images/train/example.jpg
    labels/train/example.txt

## Notes

These image files are part of the direct TrafficSigns release.

The test images are stored separately under:

    ../test/images/
