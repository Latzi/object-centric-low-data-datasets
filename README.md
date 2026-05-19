# Object-Centric Low-Data Datasets

This repository contains the public release assets for the **Object-Centric Low-Data Datasets** collection.

The collection is designed for low-data object-centric image generation and augmentation research. It contains three complementary subsets:

1. **TrafficSigns**
2. **Cityscapes--Pedestrian**
3. **COCO PottedPlant**

The release uses a **mixed-mode structure** because the three subsets have different provenance and redistribution conditions.

---

## Release overview

| Subset | Release mode | Public image files included? | Main public artifacts |
|---|---|---:|---|
| TrafficSigns | Direct release | Yes | Images, YOLO labels, manifest, metadata, checksums, loaders, examples |
| Cityscapes--Pedestrian | Abstract / non-image release | No | Scripts, manifest, annotation CSV, metadata, split documentation, checksums |
| COCO PottedPlant | Metadata / reconstruction-first release | No blanket image release | Scripts, manifest, annotation CSV, metadata, split documentation, checksums |

For more detail, see:

```text
docs/release_matrix.md
docs/dataset_card.md
docs/provenance.md
docs/ethics.md
docs/faq.md
```

---

## 1. TrafficSigns

`TrafficSigns` is the directly released subset.

The repository includes the actual released YOLO dataset structure:

```text
traffic_signs/Train_Data/
```

with:

- images
- YOLO labels
- train / validation / test split structure
- manifest CSV
- summary JSON
- checksums
- loader script
- validation example

### Current split counts

| Split | Count |
|---|---:|
| train | 2256 |
| val | 451 |
| test | 302 |
| total | 3009 |

### Class mapping

```text
0 -> TrafficSigns
```

### Main files

```text
traffic_signs/data.yaml
traffic_signs/Train_Data/
traffic_signs/metadata/traffic_signs_manifest.csv
traffic_signs/metadata/traffic_signs_summary.json
traffic_signs/checksums/traffic_signs_sha256.txt
loaders/traffic_signs.py
examples/load_traffic_signs.py
examples/validate_traffic_signs.py
```

### Quick check

From the repository root:

```bash
python examples/load_traffic_signs.py
python examples/validate_traffic_signs.py
```

---

## 2. Cityscapes--Pedestrian

`Cityscapes--Pedestrian` is a Cityscapes-derived subset.

This repository does **not** redistribute:

- original Cityscapes images
- derived cropped Cityscapes pedestrian images
- thumbnails or preview images derived from Cityscapes
- mask images derived from Cityscapes crops

Instead, the repository provides public non-image release assets:

- reconstruction / preparation scripts
- public manifest
- public per-box annotation CSV
- summary metadata
- pipeline configuration
- split documentation
- mask-generation documentation
- checksum file for public non-image artifacts

### Main files

```text
cityscapes_pedestrian/scripts/
cityscapes_pedestrian/reconstruct_cityscapes.py
cityscapes_pedestrian/manifests/cityscapes_pedestrian_manifest.csv
cityscapes_pedestrian/annotations/cityscapes_pedestrian_boxes.csv
cityscapes_pedestrian/metadata/cityscapes_pedestrian_summary.json
cityscapes_pedestrian/metadata/pipeline_config_cityscapes.json
cityscapes_pedestrian/checksums/cityscapes_pedestrian_public_sha256.txt
cityscapes_pedestrian/splits/README.md
cityscapes_pedestrian/masks/README.md
LICENSES/cityscapes_notice.txt
```

### Public manifest

The canonical public manifest is:

```text
cityscapes_pedestrian/manifests/cityscapes_pedestrian_manifest.csv
```

It contains one row per public sample record.

Current public manifest counts:

| Split | Count |
|---|---:|
| train | 1509 |
| val | 323 |
| test | 324 |
| total | 2156 |

### Public annotation table

The canonical public annotation table is:

```text
cityscapes_pedestrian/annotations/cityscapes_pedestrian_boxes.csv
```

It contains one row per pedestrian-related bounding box associated with the public manifest records.

Current public annotation-table row count:

```text
17479 boxes
```

The annotation CSV does **not** contain image pixels, cropped pedestrian images, thumbnails, preview images, or mask images. It supports:

- annotation inspection
- split-level statistics
- bounding-box mask rasterization
- consistency checks against the manifest
- local reconstruction workflows for authorized users

### Class mapping

```text
0 -> pedestrian
```

### Reconstruction notes

Users must obtain Cityscapes separately and comply with the upstream Cityscapes terms.

The local reconstruction pipeline produces image crops and YOLO labels on the user's own machine. Those locally reconstructed image files are not included in this repository.

See also:

```text
LICENSES/cityscapes_notice.txt
cityscapes_pedestrian/README.md
cityscapes_pedestrian/annotations/README.md
cityscapes_pedestrian/masks/README.md
```

---

## 3. COCO PottedPlant

`COCO PottedPlant` is an MS-COCO-derived subset built from the `potted plant` category.

This repository does **not** assume blanket redistribution rights for all COCO-derived cropped image files.

This repository does **not** redistribute:

- original MS-COCO image files
- blanket packaged COCO-derived cropped images
- thumbnails or preview images derived from COCO
- mask images derived from COCO crops

Instead, the repository provides public non-image release assets:

- reconstruction / preparation scripts
- public manifest
- public per-box annotation CSV
- summary metadata
- pipeline configuration
- split documentation
- mask-generation documentation
- checksum file for public non-image artifacts

### Main files

```text
coco_pottedplant/scripts/
coco_pottedplant/reconstruct_coco.py
coco_pottedplant/manifests/coco_pottedplant_manifest.csv
coco_pottedplant/annotations/coco_pottedplant_boxes.csv
coco_pottedplant/metadata/coco_pottedplant_summary.json
coco_pottedplant/metadata/pipeline_config_coco.json
coco_pottedplant/checksums/coco_pottedplant_public_sha256.txt
coco_pottedplant/splits/README.md
coco_pottedplant/masks/README.md
LICENSES/coco_notice.txt
```

### Public manifest

The canonical public manifest is:

```text
coco_pottedplant/manifests/coco_pottedplant_manifest.csv
```

It contains one row per public sample record.

Current public manifest counts:

| Split | Count |
|---|---:|
| train | 7380 |
| val | 299 |
| total | 7679 |

### Public annotation table

The canonical public annotation table is:

```text
coco_pottedplant/annotations/coco_pottedplant_boxes.csv
```

It contains one row per potted-plant bounding box in the locally reconstructed cropped YOLO subset.

Current public annotation-table row count:

```text
20230 boxes
```

The annotation CSV does **not** contain image pixels, cropped COCO images, thumbnails, preview images, or mask images. It supports:

- annotation inspection
- split-level statistics
- bounding-box mask rasterization
- consistency checks against the manifest
- local reconstruction workflows for users who obtain COCO separately

### Class mapping

```text
0 -> potted_plant
```

### Reconstruction notes

Users must obtain COCO images and annotations separately and comply with the upstream terms that apply to those files.

The local reconstruction pipeline produces cropped image files and YOLO labels on the user's own machine. Those locally reconstructed image files are not included as a blanket public image release in this repository.

See also:

```text
LICENSES/coco_notice.txt
coco_pottedplant/README.md
coco_pottedplant/annotations/README.md
coco_pottedplant/masks/README.md
```

---

## Repository structure

```text
object-centric-low-data-datasets/
    README.md
    CITATION.cff
    LICENSES/
    docs/
    traffic_signs/
    cityscapes_pedestrian/
    coco_pottedplant/
    loaders/
    examples/
    tools/
    zenodo/
```

Important documentation:

```text
docs/dataset_card.md
docs/release_matrix.md
docs/provenance.md
docs/ethics.md
docs/faq.md
```

---

## Installation / dependencies

The repository contains lightweight Python utilities and dataset-preparation scripts.

For TrafficSigns examples, standard Python is sufficient.

For Cityscapes and COCO reconstruction scripts, install the subset-specific requirements:

```bash
pip install -r cityscapes_pedestrian/scripts/requirements_cityscapes.txt
pip install -r coco_pottedplant/scripts/requirements_coco.txt
```

---

## Citation

Citation metadata is provided in:

```text
CITATION.cff
```

A DOI-backed archival release should be added before or at submission time.

---

## License and notices

Because the three subsets have different provenance and release conditions, licensing and redistribution notices are documented separately:

```text
LICENSES/traffic_signs_license.txt
LICENSES/cityscapes_notice.txt
LICENSES/coco_notice.txt
```

Users are responsible for complying with upstream dataset terms when reconstructing Cityscapes-derived or COCO-derived subsets.

---

## Intended use

This collection is intended for research on:

- low-data object-centric image generation
- few-shot generative modeling
- synthetic data augmentation
- object-centric representation learning
- generative model evaluation
- reconstruction-aware dataset release workflows

---

## Status

This repository is under active preparation as the public release companion for the Object-Centric Low-Data Datasets resource paper.