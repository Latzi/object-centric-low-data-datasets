# TrafficSigns Annotations

This folder contains the YOLO-format bounding-box annotations for the **TrafficSigns** subset.

## Overview

Each released image in the TrafficSigns subset has a corresponding annotation file with the **same base filename** and a `.txt` extension.

Example:

- image: `2022-04-07T06.03.45.frame1_183_86_2.jpg`
- annotation: `2022-04-07T06.03.45.frame1_183_86_2.txt`

The annotation files are stored directly in this folder.

## Class mapping

This subset uses one merged target class:

- `0` → `TrafficSigns`

The class definition is stored in:

- `classes.txt`

## Annotation format

Annotations use standard **YOLO bounding-box format**.

Each line in a `.txt` file has the form:

`class_id x_center y_center width height`

where:

- `class_id` is the numeric class label
- `x_center` is the normalized x-coordinate of the box center
- `y_center` is the normalized y-coordinate of the box center
- `width` is the normalized box width
- `height` is the normalized box height

All coordinates are normalized to the image size and lie in `[0, 1]`.

## Example

For the image:

`2022-04-07T06.03.45.frame1_183_86_2.jpg`

the corresponding annotation file may contain:

```text
0 0.650391 0.837891 0.378906 0.261719
0 0.671875 0.468750 0.476562 0.507812
