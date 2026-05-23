# TrafficSigns Metadata



This folder contains the canonical metadata files for the **TrafficSigns** subset.



## Files



- `traffic_signs_manifest.csv` — one row per released image

- `traffic_signs_summary.json` — subset-level summary information



## Purpose



The metadata in this folder provides the machine-readable description of the released TrafficSigns subset.



The manifest records:



- the released image path

- the matching annotation path

- split membership (`train`, `val`, or `test`)

- class information

- the number of annotated boxes in each image

- basic release-format information



The summary JSON records:



- subset name

- release mode

- class map

- target image size

- annotation format

- total image count

- split counts

- dataset root and YOLO config reference



## Canonical split structure



The canonical dataset layout for TrafficSigns is the YOLO-style folder structure under:



- `../Train_Data/`



and the corresponding dataset configuration file:



- `../data.yaml`



## Notes



The metadata files in this folder should stay consistent with:



- the actual files stored in `../Train_Data/`

- the YOLO label format used in `../Train_Data/labels/...`

- the class definition used in `../annotations/classes.txt`



If the dataset is updated, the manifest and summary files should be regenerated or revised accordingly.

