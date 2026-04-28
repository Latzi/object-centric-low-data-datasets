# Object-Centric Low-Data Datasets

This repository contains the release assets for a curated collection of three object-centric datasets designed for low-data image generation and augmentation.

The collection includes three subsets:

- **Traffic Signs**
- **Cityscapes--Pedestrian**
- **COCO PottedPlant**

These subsets were curated to support research on object-centric generative modelling in low-data regimes, including settings with blur, occlusion, and diverse background complexity.

## Repository purpose

The goal of this repository is to provide a reproducible release package for the dataset collection described in our resource paper. Depending on upstream licensing conditions, each subset is released either as:

- a **direct dataset release**, or
- a **metadata / reconstruction-style release** with annotations, split files, metadata, and scripts.

## Release mode by subset

| Subset | Release mode | Notes |
|---|---|---|
| Traffic Signs | Direct release | Author-owned subset |
| Cityscapes--Pedestrian | Abstract / non-image release | Cropped images are not redistributed |
| COCO PottedPlant | Metadata / reconstruction-first release | No blanket cropped-image redistribution |

See [`docs/release_matrix.md`](docs/release_matrix.md) for a fuller explanation.

## What is included in this repository

This repository is organized around three subset folders and shared support files:

- `traffic_signs/` – directly released Traffic Signs subset
- `cityscapes_pedestrian/` – non-image release assets for the Cityscapes-derived subset
- `coco_pottedplant/` – metadata / reconstruction assets for the COCO-derived subset
- `loaders/` – dataset loading utilities
- `examples/` – usage examples and quickstart material
- `tools/` – validation and utility scripts
- `docs/` – dataset card, provenance, ethics, and release notes

## Current status

This repository is being prepared as the public release companion for the dataset collection. The structure is in place and subset-specific files are being added progressively.

## Planned contents by subset

### Traffic Signs
Planned contents include:
- images
- annotations
- masks
- split files
- metadata
- checksums
- example loaders

### Cityscapes--Pedestrian
Planned contents include:
- annotations
- masks or derived labels (where appropriate)
- split files
- manifests
- metadata
- checksums
- reconstruction / preparation tooling

### COCO PottedPlant
Planned contents include:
- annotations
- split files
- manifests
- metadata
- checksums
- reconstruction / preparation tooling

## Documentation

Additional documentation will be provided in:

- [`docs/dataset_card.md`](docs/dataset_card.md)
- [`docs/provenance.md`](docs/provenance.md)
- [`docs/ethics.md`](docs/ethics.md)
- [`docs/release_matrix.md`](docs/release_matrix.md)

## Citation

Citation information for this repository will be added in `CITATION.cff` and in the archived DOI release.

## License and notices

Because the three subsets have different provenance and release conditions, licensing and redistribution notices are documented separately in:

- `LICENSES/traffic_signs_license.txt`
- `LICENSES/cityscapes_notice.txt`
- `LICENSES/coco_notice.txt`



