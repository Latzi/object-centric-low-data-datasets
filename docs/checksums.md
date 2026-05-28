# Checksums and Release Verification

This document explains checksum handling for the **Object-Centric Low-Data Datasets** release.

Checksum files are included so users can verify public release artifacts after downloading or reconstructing the repository archive.

## Checksum files

The release contains subset-level checksum files:

```text
traffic_signs/checksums/traffic_signs_sha256.txt
cityscapes_pedestrian/checksums/cityscapes_pedestrian_public_sha256.txt
coco_pottedplant/checksums/coco_pottedplant_public_sha256.txt
```

## What the checksums cover

### TrafficSigns

The TrafficSigns checksum file covers public direct-release artifacts under the `traffic_signs/` folder, including images, YOLO labels, metadata, manifests, documentation, and related release files.

### Cityscapes--Pedestrian

The Cityscapes--Pedestrian checksum file covers public non-image release artifacts under the `cityscapes_pedestrian/` folder, including scripts, manifests, public annotation CSVs, metadata, documentation, and reconstruction assets.

It does not cover original Cityscapes images or locally reconstructed Cityscapes crop images, because those are not redistributed in this repository.

### COCO PottedPlant

The COCO PottedPlant checksum file covers public reconstruction-first release artifacts under the `coco_pottedplant/` folder, including scripts, manifests, public annotation CSVs, metadata, documentation, and reconstruction assets.

It does not cover original COCO images or locally reconstructed COCO crop images, because those are not redistributed as a blanket public image release.

## Verification command

From the repository root, run:

```bash
python tools/verify_release_checksums.py
```

On Windows PowerShell:

```powershell
python tools\verify_release_checksums.py
```

Expected result:

```text
Checksum verification PASSED.
```

## Notes

Checksums verify file integrity. They do not grant rights to upstream datasets.

Users must obtain Cityscapes and COCO data separately where required and comply with the corresponding upstream terms.
