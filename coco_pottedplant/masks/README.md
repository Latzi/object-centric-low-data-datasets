\# COCO PottedPlant Masks



This folder documents mask handling for the \*\*COCO PottedPlant\*\* subset.



Explicit binary mask image files are not distributed in this repository.



Instead, bounding-box masks can be generated from the YOLO-format bounding-box annotations produced by the local reconstruction pipeline.



\## Why masks are not stored here



The COCO PottedPlant subset is released in metadata / reconstruction-first form. This repository does not assume blanket redistribution rights for all COCO-derived image or mask files.



\## How to obtain masks



After reconstructing the subset locally from upstream COCO data, users can rasterize binary masks from the cropped YOLO bounding boxes.



For a `256x256` crop, a BB mask is a binary image where pixels inside a potted-plant bounding box are set to `1` and pixels outside the box are set to `0`.



\## Related files



\- `../annotations/`

\- `../manifests/coco\_pottedplant\_manifest.csv`

\- `../scripts/`

\- `../../LICENSES/coco\_notice.txt`

