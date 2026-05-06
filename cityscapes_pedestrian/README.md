# \# Cityscapes--Pedestrian

# 

# This folder contains the \*\*Cityscapes--Pedestrian\*\* subset of the \*\*Object-Centric Low-Data Datasets\*\* collection.

# 

# \## Summary

# 

# Cityscapes--Pedestrian is a Cityscapes-derived object-centric subset designed for low-data image generation and augmentation research.

# 

# In the FDGAN setup, this subset is created from high-resolution Cityscapes frames by merging pedestrian-related classes into a unified pedestrian category and extracting `256×256` crops around detected objects. The resulting subset represents the most challenging regime in the collection, with dense scenes, overlap, occlusion, privacy blur, and visually complex urban backgrounds. :contentReference\[oaicite:2]{index=2}

# 

# \## Why this subset matters

# 

# Compared with the other subsets in the collection, Cityscapes--Pedestrian is the most difficult visual regime:

# 

# \- dense pedestrian scenes

# \- frequent overlap and occlusion

# \- privacy-blurred faces

# \- cluttered urban backgrounds

# \- greater structural ambiguity than simpler object-centric datasets

# 

# This makes the subset useful for studying low-data object-centric generation under degraded real-world conditions.

# 

# \## Release mode

# 

# This subset is released in \*\*abstract / non-image form\*\*.

# 

# That means this repository does \*\*not\*\* redistribute:

# 

# \- original Cityscapes image files

# \- cropped pedestrian image patches derived from Cityscapes

# \- thumbnails or substitute image exports

# 

# Instead, this folder is intended to contain:

# 

# \- annotations

# \- split files

# \- manifests

# \- metadata

# \- checksums

# \- preparation / reconstruction scripts

# \- documentation

# 

# \## Intended structure

# 

# The intended contents of this folder are:

# 

# \- `annotations/` — released non-image annotation artifacts

# \- `masks/` — derived mask artifacts where appropriate

# \- `splits/` — split definitions or split documentation

# \- `manifests/` — canonical machine-readable subset manifests

# \- `metadata/` — subset-level metadata and summary files

# \- `checksums/` — integrity files for released artifacts

# \- `reconstruct\_cityscapes.py` — preparation / reconstruction tooling

# 

# \## Notes on upstream dependency

# 

# Users who wish to work with this subset must obtain access to the original Cityscapes dataset separately and comply with the official upstream terms.

# 

# This repository does not grant rights to the underlying Cityscapes image data.

# 

# See also:

# 

# \- `../LICENSES/cityscapes\_notice.txt`

# 

# \## Notes

# 

# The canonical public artifacts for this subset are the non-image release assets stored in this folder. These assets should remain consistent with the documentation in:

# 

# \- `../docs/release\_matrix.md`

# \- `../docs/dataset\_card.md`

