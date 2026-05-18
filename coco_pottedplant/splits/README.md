\# COCO PottedPlant Splits



This folder documents the split structure for the \*\*COCO PottedPlant\*\* subset.



\## Purpose



Because this subset is released in \*\*metadata / reconstruction-first form\*\*, the split layer is documented here as part of the public release package.



The purpose of this folder is to describe how released records are assigned to upstream-derived split groups without assuming blanket redistribution of the underlying source images.



\## Canonical split definition



The current COCO PottedPlant pipeline preserves the original COCO split structure used during extraction and cropping.



At present, the canonical split values are:



\- `train`

\- `val`



These split values should be reflected in:



\- `../manifests/coco\_pottedplant\_manifest.csv`



If additional split files are added later, they should remain consistent with that manifest.



\## Current pipeline behavior



\### Step 01

`01\_extract\_pottedplant\_from\_coco\_to\_yolo.py` extracts potted-plant instances from the official COCO `train2017` and `val2017` splits and writes a YOLO full-image subset.



\### Step 02

`02\_create\_instance\_crops\_from\_yolo\_pottedplant.py` creates `256×256` per-instance crops while preserving the split membership inherited from Step 01.



\## What this folder may contain



This folder may contain:



\- split documentation

\- optional text-based split lists

\- release notes about split construction

\- mapping files that associate released sample identifiers with split membership



\## What this folder should NOT contain



This folder should not contain:



\- original MS-COCO image files

\- blanket packaged cropped image subsets

\- preview images or thumbnails

\- artifacts intended to substitute for the underlying source data



\## Notes



The current public package documents `train` and `val` split membership only.



If a future version of the local authorized workflow introduces an additional test split, this folder and the public manifest should be updated accordingly.



See also:



\- `../README.md`

\- `../manifests/coco\_pottedplant\_manifest.csv`

\- `../metadata/coco\_pottedplant\_summary.json`

\- `../scripts/README.md`

\- `../../LICENSES/coco\_notice.txt`

