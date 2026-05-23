# Cityscapes--Pedestrian Splits



This folder documents the split structure for the **Cityscapes--Pedestrian** subset.



## Purpose



Because this subset is released in **abstract / non-image form**, the split layer is documented here as part of the public release package.



The purpose of this folder is to describe how released records are assigned to training, validation, and test subsets without redistributing the underlying Cityscapes image data.



## Canonical split definition



The canonical split membership for public records should be reflected in:



- `../manifests/cityscapes_pedestrian_manifest.csv`



If additional split files are added later, they should remain consistent with that manifest.



## Expected split values



Released records should use one of the following split labels:



- `train`

- `val`

- `test`



## What this folder may contain



This folder may contain:



- split documentation

- optional text-based split lists

- release notes about split construction

- mapping files that associate released sample identifiers with split membership



## What this folder should NOT contain



This folder should not contain:



- Cityscapes image files

- cropped pedestrian images

- preview images or thumbnails

- any artifact that substitutes for the released image subset



## Notes



The split definitions documented here are part of the public non-image release and should remain consistent with:



- `../README.md`

- `../metadata/cityscapes_pedestrian_summary.json`

- `../manifests/cityscapes_pedestrian_manifest.csv`

- `../../LICENSES/cityscapes_notice.txt`

