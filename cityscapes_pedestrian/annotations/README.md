\# Cityscapes--Pedestrian Annotations



This folder documents the annotation layer for the \*\*Cityscapes--Pedestrian\*\* subset.



\## Purpose



Because this subset is released in \*\*abstract / non-image form\*\*, annotation artifacts released here are limited to non-image metadata and derived annotation information that does not redistribute Cityscapes image content.



\## Intended annotation role



The annotation layer is intended to support:



\- class mapping

\- released sample identifiers

\- split-aware annotation lookup

\- derived non-image artifact tracking

\- consistency with the public manifest and metadata files



\## Class definition



The Cityscapes--Pedestrian subset uses a merged pedestrian class derived from pedestrian-related categories in the upstream dataset.



Public release notation for this subset should use:



\- `0` → `pedestrian`



\## What may be included here



This folder may contain:



\- class mapping files

\- non-image annotation tables

\- derived label metadata

\- annotation documentation

\- mapping files that connect released sample identifiers to annotation artifacts



\## What should NOT be included here



This folder should not contain:



\- original Cityscapes images

\- cropped pedestrian image patches

\- thumbnails or previews

\- image-derived artifacts intended to substitute for the released image subset



\## Relationship to other files



The annotation layer should remain consistent with:



\- `../README.md`

\- `../manifests/cityscapes\_pedestrian\_manifest.csv`

\- `../metadata/cityscapes\_pedestrian\_summary.json`

\- `../splits/README.md`



See also:



\- `../../LICENSES/cityscapes\_notice.txt`



\## Notes



If concrete annotation files are added later, this folder should make clear which files are canonical public annotation artifacts for the non-image release.

