\# Cityscapes--Pedestrian Manifests



This folder contains the canonical manifest documentation for the \*\*Cityscapes--Pedestrian\*\* subset.



\## Purpose



Because this subset is released in \*\*abstract / non-image form\*\*, the manifest is one of the key public artifacts.



The manifest is intended to describe the released subset in a machine-readable way without redistributing the underlying Cityscapes image data.



\## What a manifest records



A Cityscapes--Pedestrian manifest should record, for each released sample or subset entry:



\- a stable released sample identifier

\- the upstream source image identifier

\- split membership

\- class information

\- crop metadata

\- bounding-box metadata

\- references to any released non-image artifacts

\- notes about filtering or processing status



\## What a manifest should NOT contain



The manifest should not be used as a substitute for redistributing Cityscapes image data.



This folder should not contain:



\- original Cityscapes images

\- cropped pedestrian image patches

\- thumbnails or preview images

\- any artifact intended to replicate the released image subset itself



\## Intended manifest role in this repository



The Cityscapes--Pedestrian manifest is intended to support:



\- reproducibility

\- split tracking

\- metadata lookup

\- consistency checks across released annotations and derived artifacts

\- preparation / reconstruction workflows used by authorized users with upstream dataset access



\## Related files



The manifest layer in this folder should remain consistent with:



\- `../README.md`

\- `../metadata/`

\- `../splits/`

\- `../annotations/`

\- `../reconstruct\_cityscapes.py`



See also:



\- `../../LICENSES/cityscapes\_notice.txt`



\## Notes



If multiple manifest files are added later, this folder should make clear which one is the canonical public release manifest.

