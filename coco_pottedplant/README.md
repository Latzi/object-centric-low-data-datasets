# \# COCO PottedPlant

# 

# This folder contains the \*\*COCO PottedPlant\*\* subset of the \*\*Object-Centric Low-Data Datasets\*\* collection.

# 

# \## Summary

# 

# COCO PottedPlant is an MS-COCO-derived object-centric subset designed for low-data image generation and augmentation research.

# 

# In the FDGAN setup, this subset is created from \*\*MS-COCO 2017\*\* by selecting the \*\*potted plant\*\* category and generating `256×256` crops on a per-instance basis. Each crop is formed so that the selected plant instance lies inside the crop with a random margin or offset, which means the object is not always centered and the surrounding context varies across samples. The resulting subset exposes diverse indoor and outdoor backgrounds, variable object placement, and greater contextual variability than the simpler TrafficSigns subset. :contentReference\[oaicite:2]{index=2}

# 

# \## Why this subset matters

# 

# Compared with the other subsets in the collection, COCO PottedPlant provides the most context-diverse visual regime:

# 

# \- indoor and outdoor scenes

# \- variable background complexity

# \- variable object placement

# \- per-instance crop construction

# \- possible overlap between crops when plants are close

# 

# This makes the subset useful for studying low-data object-centric generation under strong contextual variability.

# 

# \## Release mode

# 

# This subset is released in \*\*metadata / reconstruction-first form\*\*.

# 

# That means this repository is intended to provide:

# 

# \- annotations

# \- split files or split documentation

# \- manifests

# \- metadata

# \- checksums

# \- preparation / reconstruction scripts

# \- documentation

# 

# rather than directly redistributing a blanket packaged image subset.

# 

# \## Intended structure

# 

# The intended contents of this folder are:

# 

# \- `annotations/` — non-image annotation artifacts

# \- `masks/` — derived mask artifacts where appropriate

# \- `splits/` — split definitions or split documentation

# \- `manifests/` — canonical machine-readable subset manifests

# \- `metadata/` — subset-level metadata and summary files

# \- `checksums/` — integrity files for released artifacts

# \- `reconstruct\_coco.py` — preparation / reconstruction tooling

# 

# \## Notes on upstream dependency

# 

# Users who wish to work with this subset must obtain the upstream COCO images separately and comply with the original upstream terms that apply to those files.

# 

# This repository does not grant rights to the underlying upstream image data.

# 

# See also:

# 

# \- `../LICENSES/coco\_notice.txt`

# 

# \## Notes

# 

# The canonical public artifacts for this subset are the non-image release assets stored in this folder. These assets should remain consistent with the documentation in:

# 

# \- `../docs/release\_matrix.md`

# \- `../docs/dataset\_card.md`

