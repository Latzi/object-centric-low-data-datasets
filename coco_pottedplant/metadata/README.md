\# COCO PottedPlant Metadata



This folder contains the subset-level metadata files for the \*\*COCO PottedPlant\*\* subset.



\## Purpose



Because this subset is released in \*\*metadata / reconstruction-first form\*\*, metadata files in this folder provide the high-level structured description of the released subset without assuming blanket redistribution of the underlying upstream image files.



\## Intended contents



This folder is intended to contain subset-level metadata such as:



\- summary JSON files

\- subset statistics

\- release-mode descriptors

\- class mapping information

\- references to the canonical public manifest



\## Relationship to other files



The metadata files in this folder should remain consistent with:



\- `../README.md`

\- `../manifests/coco\_pottedplant\_manifest.csv`

\- `../splits/`

\- `../annotations/`

\- `../reconstruct\_coco.py`



\## What metadata should describe



Subset-level metadata should document:



\- subset name

\- release mode

\- class mapping

\- expected crop size

\- source dataset and source category

\- per-instance crop construction assumptions

\- split counts

\- links to canonical manifest files

\- notes on upstream dependency and redistribution constraints



\## What does NOT belong here



This folder should not contain:



\- original MS-COCO image files

\- blanket packaged image crops

\- preview images or thumbnails

\- image-derived artifacts intended to substitute for the source data



\## Notes



The metadata in this folder is part of the public non-image / reconstruction-first release and should remain consistent with the licensing and release notices for the COCO-derived subset.



See also:



\- `../../LICENSES/coco\_notice.txt`

\- `../../docs/release\_matrix.md`

\- `../../docs/dataset\_card.md`

