\# Cityscapes--Pedestrian Metadata



This folder contains the subset-level metadata files for the \*\*Cityscapes--Pedestrian\*\* subset.



\## Purpose



Because this subset is released in \*\*abstract / non-image form\*\*, metadata files in this folder provide the high-level structured description of the released subset without redistributing the underlying Cityscapes image data.



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

\- `../manifests/cityscapes\_pedestrian\_manifest.csv`

\- `../splits/`

\- `../annotations/`

\- `../reconstruct\_cityscapes.py`



\## What metadata should describe



Subset-level metadata should document:



\- subset name

\- release mode

\- class mapping

\- expected crop size

\- detector / preprocessing settings where appropriate

\- split counts

\- links to canonical manifest files

\- notes on upstream dependency and redistribution constraints



\## What does NOT belong here



This folder should not contain:



\- original Cityscapes images

\- cropped pedestrian image files

\- preview images or thumbnails

\- image-derived artifacts intended to substitute for the source data



\## Notes



The metadata in this folder is part of the public non-image release and should be safe to distribute under the repository’s release model for the Cityscapes-derived subset.



See also:



\- `../../LICENSES/cityscapes\_notice.txt`

\- `../../docs/release\_matrix.md`

\- `../../docs/dataset\_card.md`

