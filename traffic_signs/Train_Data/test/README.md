# TrafficSigns Test Split

This folder contains the TrafficSigns test split.

## Layout

    test/
        images/
        labels/

## Contents

The `images/` folder contains released TrafficSigns test images.

The `labels/` folder contains corresponding YOLO-format annotation files.

Each test image should have a matching label file with the same base filename.

For example:

    test/images/example.jpg
    test/labels/example.txt

## Split count

| Split | Count |
|---|---:|
| test | 302 |

## Class mapping

    0 -> TrafficSigns

## Notes

The test split is part of the direct TrafficSigns release and is included in the canonical metadata summary.
