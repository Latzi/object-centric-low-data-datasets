# TrafficSigns Annotations

This folder contains the annotation-level documentation for the **TrafficSigns** subset.

## What is stored here

This folder stores:

- `classes.txt` â€” the class mapping for the subset
- this `README.md` file â€” documentation for the annotation format and layout

## Class mapping

The subset uses one merged target class:

- `0` â†’ `TrafficSigns`

The class definition is stored in:

- `classes.txt`

## Where the actual YOLO label files are

The canonical released YOLO label files are stored under the `Train_Data/` directory, not in this folder.

They are located in:

- `../Train_Data/labels/train/`
- `../Train_Data/labels/val/`
- `../Train_Data/test/labels/`

Each label file has the same base filename as its corresponding image.

Example:

- image: `../Train_Data/images/train/2022-04-07T06.03.45.frame1_183_86_2.jpg`
- label: `../Train_Data/labels/train/2022-04-07T06.03.45.frame1_183_86_2.txt`

## YOLO annotation format

Annotations use standard YOLO bounding-box format.

Each line in a label file has the form:

`class_id x_center y_center width height`

where:

- `class_id` is the numeric class label
- `x_center` is the normalized x-coordinate of the box center
- `y_center` is the normalized y-coordinate of the box center
- `width` is the normalized box width
- `height` is the normalized box height

All coordinates are normalized to the image size and lie in `[0, 1]`.

## Notes

- Most TrafficSigns images contain one clearly visible object, but some contain multiple annotated traffic signs.
- The metadata manifest in `../metadata/traffic_signs_manifest.csv` records the released image path, matching label path, split membership, and number of boxes per image.
- The canonical split definition is documented in `../splits/README.md`.

## Annotation provenance

The TrafficSigns labels originate from a detector-assisted annotation workflow.

Candidate bounding boxes for `Traffic Sign` and `Damaged Traffic Sign` objects were generated using YOLOv5x and manually reviewed before release.

The released YOLO-format labels are therefore the canonical reviewed annotation layer for this subset, not raw detector output.
