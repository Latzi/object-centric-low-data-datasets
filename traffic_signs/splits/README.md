# TrafficSigns Splits



This folder documents the split structure used for the **TrafficSigns** subset.



## Canonical split definition



The canonical split for TrafficSigns is defined by the YOLO-style folder structure under:



- `../Train_Data/`



and by the dataset configuration file:



- `../data.yaml`



## Split layout



The released split layout is:



- `../Train_Data/images/train/`

- `../Train_Data/images/val/`

- `../Train_Data/test/images/`



with matching YOLO label files in:



- `../Train_Data/labels/train/`

- `../Train_Data/labels/val/`

- `../Train_Data/test/labels/`



## Interpretation



- files in `images/train/` belong to the training split

- files in `images/val/` belong to the validation split

- files in `test/images/` belong to the test split



The matching label file for each image must have the same base filename and be located in the corresponding label folder.



## Notes



This repository uses the YOLO directory layout itself as the authoritative split definition for TrafficSigns.



The metadata manifest in:



- `../metadata/traffic_signs_manifest.csv`



records the split membership for each released image.



If text-based split lists are needed in the future, they can be generated from the manifest or from the directory structure, but they are not the primary split definition in this release.

