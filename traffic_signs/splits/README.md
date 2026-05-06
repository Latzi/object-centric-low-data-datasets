\# TrafficSigns Splits



This folder documents the split structure used for the \*\*TrafficSigns\*\* subset.



\## Canonical split definition



The canonical split for TrafficSigns is defined by the YOLO-style folder structure under:



\- `../Train\_Data/`



and by the dataset configuration file:



\- `../data.yaml`



\## Split layout



The released split layout is:



\- `../Train\_Data/images/train/`

\- `../Train\_Data/images/val/`

\- `../Train\_Data/test/images/`



with matching YOLO label files in:



\- `../Train\_Data/labels/train/`

\- `../Train\_Data/labels/val/`

\- `../Train\_Data/test/labels/`



\## Interpretation



\- files in `images/train/` belong to the training split

\- files in `images/val/` belong to the validation split

\- files in `test/images/` belong to the test split



The matching label file for each image must have the same base filename and be located in the corresponding label folder.



\## Notes



This repository uses the YOLO directory layout itself as the authoritative split definition for TrafficSigns.



The metadata manifest in:



\- `../metadata/traffic\_signs\_manifest.csv`



records the split membership for each released image.



If text-based split lists are needed in the future, they can be generated from the manifest or from the directory structure, but they are not the primary split definition in this release.

