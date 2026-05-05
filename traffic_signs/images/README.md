# TrafficSigns Images

This folder contains the final released **256×256 crop images** for the TrafficSigns subset.

## What belongs here

This folder should contain the final object-centric crop images that are part of the released dataset.

Each image in this folder should:

- be a final released crop
- have size `256×256`
- have a matching YOLO annotation file with the same base filename in `../annotations/`

Example:

- image: `2022-04-07T06.03.45.frame1_183_86_2.jpg`
- annotation: `../annotations/2022-04-07T06.03.45.frame1_183_86_2.txt`

## What does NOT belong here

This folder should not contain:

- original larger source frames
- intermediate preprocessing outputs
- duplicate files
- images that are not part of the final released subset

## Notes

The original source-image information and crop provenance should be tracked through metadata files rather than by storing the raw source frames in this release folder.****
