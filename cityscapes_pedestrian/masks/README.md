\# Cityscapes--Pedestrian Masks



This folder documents mask handling for the \*\*Cityscapes--Pedestrian\*\* subset.



Explicit binary mask image files are not distributed in this repository.



Instead, bounding-box masks are generated from the released or locally reconstructed bounding-box annotations when required by BB-guided generative models.



\## Why masks are not stored here



The Cityscapes--Pedestrian subset is released in abstract / non-image form. This repository does not redistribute:



\- original Cityscapes images

\- derived Cityscapes crop images

\- mask images derived from Cityscapes crops



\## How to obtain masks



After reconstructing the subset locally from authorized Cityscapes data, users can rasterize binary masks from the YOLO-format bounding boxes.



For a `256x256` crop, a BB mask is a binary image where pixels inside the bounding box are set to `1` and pixels outside the box are set to `0`.



\## Related files



\- `../annotations/`

\- `../manifests/cityscapes\_pedestrian\_manifest.csv`

\- `../scripts/`

\- `../../LICENSES/cityscapes\_notice.txt`

