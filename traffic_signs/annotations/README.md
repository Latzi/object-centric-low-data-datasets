# Traffic Signs Annotations

This folder contains bounding-box annotations for the Traffic Signs subset.

## Class mapping

The subset uses one merged class:

- `0` → `traffic_sign`

## Annotation format

The primary release format is YOLO text annotation format.

Each image has a corresponding label file in:

- `annotations/yolo/`

For an image named:

`images/TS_000001.png`

the corresponding label file should be:

`annotations/yolo/TS_000001.txt`

## YOLO label format

Each line in a label file has the form:

`class_id x_center y_center width height`

where coordinates are normalized to the image size and lie in `[0, 1]`.

Example:

`0 0.512 0.487 0.231 0.164`

## Notes

Most Traffic Signs samples are expected to contain a single clearly isolated object, but the format supports multiple lines per image if needed.
