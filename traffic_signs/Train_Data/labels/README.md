# TrafficSigns Train and Validation Labels

This folder contains YOLO-format label files for the TrafficSigns training and validation images.

## Layout

    labels/
        train/
        val/

## Matching images

Matching image files are stored under:

    ../images/train/
    ../images/val/

Each label file should correspond to an image with the same base filename.

For example:

    images/train/example.jpg
    labels/train/example.txt

## YOLO annotation format

Each annotation line has the form:

    class_id x_center y_center width height

Coordinates are normalized to the image size and should lie in the range `[0, 1]`.

## Class mapping

    0 -> TrafficSigns

## Notes

A label file may contain one or more bounding boxes.

The test labels are stored separately under:

    ../test/labels/
