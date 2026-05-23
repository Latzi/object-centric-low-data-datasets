# COCO PottedPlant Manifests



This folder contains the canonical manifest documentation for the **COCO PottedPlant** subset.



## Purpose



Because this subset is released in **metadata / reconstruction-first form**, the manifest is one of the key public artifacts.



The manifest is intended to describe the released subset in a machine-readable way without assuming blanket redistribution of the underlying upstream image files.



## What a manifest records



A COCO PottedPlant manifest should record, for each released sample or subset entry:



- a stable released sample identifier

- the upstream source image identifier

- split membership

- class information

- crop metadata

- bounding-box metadata

- references to any released non-image artifacts

- notes about filtering or processing status



## What a manifest should NOT contain



The manifest should not be used as a substitute for redistributing a packaged upstream image subset.



This folder should not contain:



- original MS-COCO image files

- cropped potted-plant image patches released as a blanket image package

- thumbnails or preview images

- any artifact intended to replicate the image subset itself without regard to upstream image rights



## Intended manifest role in this repository



The COCO PottedPlant manifest is intended to support:



- reproducibility

- split tracking

- metadata lookup

- consistency checks across released annotations and derived artifacts

- preparation / reconstruction workflows used by users who obtain upstream images separately



## Related files



The manifest layer in this folder should remain consistent with:



- `../README.md`

- `../metadata/`

- `../splits/`

- `../annotations/`

- `../reconstruct_coco.py`



See also:



- `../../LICENSES/coco_notice.txt`



## Notes



If multiple manifest files are added later, this folder should make clear which one is the canonical public release manifest.

