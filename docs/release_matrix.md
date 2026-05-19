# Release Matrix

This document summarizes the release mode for each subset in the **Object-Centric Low-Data Datasets** collection.

The collection uses a **mixed release model** because the three subsets have different provenance, ownership, privacy, and redistribution conditions.

The purpose of this file is to answer:

1. Which subset includes public image files?
2. Which subset must be reconstructed locally?
3. What artifacts are available in this repository?
4. What upstream data must users obtain separately?
5. What public annotation files are released?

For the longer dataset description, see:

```text
docs/dataset_card.md
```

For source and processing history, see:

```text
docs/provenance.md
```

---

## 1. Summary table

| Subset | Release mode | Public image files included? | Main public artifacts | Upstream data required? |
|---|---|---:|---|---:|
| TrafficSigns | Direct release | Yes | Images, YOLO labels, manifest, metadata, checksums, loaders, examples | No |
| Cityscapes--Pedestrian | Abstract / non-image release | No | Scripts, manifest, annotation CSV, metadata, split documentation, masks documentation, checksums | Yes |
| COCO PottedPlant | Metadata / reconstruction-first release | No blanket image release | Scripts, manifest, annotation CSV, metadata, split documentation, masks documentation, checksums | Yes |

---

## 2. Meaning of release modes

### Direct release

A **direct release** means that the dataset files themselves are included in the repository or associated release archive.

In this collection, this applies to:

```text
TrafficSigns
```

Users can work directly with the released image and label files.

### Abstract / non-image release

An **abstract / non-image release** means that the repository provides non-image artifacts such as:

- scripts
- manifests
- public annotation tables
- metadata
- split documentation
- mask-generation documentation
- checksums
- reconstruction instructions

but does **not** redistribute upstream-derived image files.

In this collection, this applies to:

```text
Cityscapes--Pedestrian
```

Users must obtain the upstream Cityscapes dataset separately.

### Metadata / reconstruction-first release

A **metadata / reconstruction-first release** means that the repository provides the code, manifests, public annotation tables, and metadata needed to reconstruct the subset locally, but does not assume blanket permission to redistribute all derived images.

In this collection, this applies to:

```text
COCO PottedPlant
```

Users must obtain the upstream COCO data separately.

---

## 3. TrafficSigns

### Release mode

```text
direct_release
```

### What is included

The repository includes the actual released YOLO dataset structure:

```text
traffic_signs/Train_Data/
```

This includes:

- image files
- YOLO label files
- train / validation / test split structure
- manifest CSV
- summary JSON
- checksum file
- loader script
- load example
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

### User action

Users can use this subset directly from the repository or release archive.

---

## 4. Cityscapes--Pedestrian

### Release mode

```text
abstract_non_image
```

### What is included

The repository includes:

- reconstruction / preparation scripts
- public manifest
- public per-box annotation CSV
- summary metadata
- pipeline configuration
- split documentation
- annotation documentation
- mask-generation documentation
- checksum file for public non-image artifacts
- upstream license notice

### What is not included

The repository does **not** include:

- original Cityscapes images
- derived cropped Cityscapes pedestrian images
- thumbnails or preview images derived from Cityscapes
- mask images derived from Cityscapes crops
- any image-derived artifact intended to substitute for the Cityscapes image subset

### Current public manifest counts

| Split | Count |
|---|---:|
| train | 1509 |
| val | 323 |
| test | 324 |
| total | 2156 |

### Public annotation table

The public per-box annotation table is:

```text
cityscapes_pedestrian/annotations/cityscapes_pedestrian_boxes.csv
```

This table contains one row per pedestrian-related bounding box associated with the public manifest records.

Current annotation-table row count:

```text
17479 boxes
```

The annotation table does **not** contain image pixels or cropped Cityscapes images.

### Class mapping

```text
0 -> pedestrian
```

### Main files

```text
cityscapes_pedestrian/scripts/
cityscapes_pedestrian/reconstruct_cityscapes.py
cityscapes_pedestrian/manifests/cityscapes_pedestrian_manifest.csv
cityscapes_pedestrian/annotations/cityscapes_pedestrian_boxes.csv
cityscapes_pedestrian/metadata/cityscapes_pedestrian_summary.json
cityscapes_pedestrian/metadata/pipeline_config_cityscapes.json
cityscapes_pedestrian/splits/README.md
cityscapes_pedestrian/masks/README.md
cityscapes_pedestrian/checksums/cityscapes_pedestrian_public_sha256.txt
LICENSES/cityscapes_notice.txt
```

### User action

Users must obtain Cityscapes separately and comply with the upstream Cityscapes terms.

The scripts can then be used to reconstruct the local image crops and YOLO labels on the user's own machine.

---

## 5. COCO PottedPlant

### Release mode

```text
metadata_reconstruction_first
```

### What is included

The repository includes:

- reconstruction / preparation scripts
- public manifest
- public per-box annotation CSV
- summary metadata
- pipeline configuration
- split documentation
- annotation documentation
- mask-generation documentation
- checksum file for public non-image artifacts
- upstream license notice

### What is not included

The repository does **not** assume blanket redistribution rights for:

- original MS-COCO image files
- all derived cropped COCO image files
- thumbnails or preview images derived from COCO images
- mask images derived from COCO crops
- any image-derived artifact intended to substitute for the COCO image subset

### Current public manifest counts

| Split | Count |
|---|---:|
| train | 7380 |
| val | 299 |
| total | 7679 |

### Public annotation table

The public per-box annotation table is:

```text
coco_pottedplant/annotations/coco_pottedplant_boxes.csv
```

This table contains one row per potted-plant bounding box in the locally reconstructed cropped YOLO subset.

Current annotation-table row count:

```text
20230 boxes
```

The annotation table does **not** contain image pixels or cropped COCO images.

### Class mapping

```text
0 -> potted_plant
```

### Main files

```text
coco_pottedplant/scripts/
coco_pottedplant/reconstruct_coco.py
coco_pottedplant/manifests/coco_pottedplant_manifest.csv
coco_pottedplant/annotations/coco_pottedplant_boxes.csv
coco_pottedplant/metadata/coco_pottedplant_summary.json
coco_pottedplant/metadata/pipeline_config_coco.json
coco_pottedplant/splits/README.md
coco_pottedplant/masks/README.md
coco_pottedplant/checksums/coco_pottedplant_public_sha256.txt
LICENSES/coco_notice.txt
```

### User action

Users must obtain the upstream COCO images and annotations separately and comply with the upstream terms that apply to those files.

The scripts can then be used to reconstruct the cropped image subset and YOLO labels on the user's own machine.

---

## 6. Practical use guide

### I want to use TrafficSigns

Use the files directly under:

```text
traffic_signs/Train_Data/
```

and the YOLO config:

```text
traffic_signs/data.yaml
```

### I want to use Cityscapes--Pedestrian

Use the reconstruction scripts and public metadata under:

```text
cityscapes_pedestrian/
```

but obtain the upstream Cityscapes data separately.

The public annotation table is available at:

```text
cityscapes_pedestrian/annotations/cityscapes_pedestrian_boxes.csv
```

### I want to use COCO PottedPlant

Use the reconstruction scripts and public metadata under:

```text
coco_pottedplant/
```

but obtain the upstream COCO 2017 data separately.

The public annotation table is available at:

```text
coco_pottedplant/annotations/coco_pottedplant_boxes.csv
```

---

## 7. Public artifacts vs local reconstruction outputs

### Public artifacts

Public artifacts are files included in this repository or associated public release.

They include:

- directly releasable TrafficSigns files
- scripts
- manifests
- public per-box annotation CSVs
- summary metadata
- pipeline configuration files
- split documentation
- mask-generation documentation
- checksum files
- license notices
- responsible-use documentation

### Local reconstruction outputs

Local reconstruction outputs are generated by users on their own machines after obtaining the relevant upstream data.

They may include:

- Cityscapes-derived crops
- COCO-derived crops
- local YOLO labels
- local training-ready folders
- debug images with bounding boxes
- intermediate image folders

Local reconstruction outputs are not automatically redistributable.

---

## 8. Why the release is mixed-mode

The three subsets do not have the same redistribution situation.

- **TrafficSigns** can be released directly.
- **Cityscapes--Pedestrian** is derived from Cityscapes, so public release is limited to non-image artifacts.
- **COCO PottedPlant** is derived from COCO/Flickr images, so the repository provides reconstruction assets and metadata rather than assuming blanket image redistribution rights.

This design aims to maximize reproducibility while respecting upstream dataset conditions.

---

## 9. Related documentation

For fuller details, see:

```text
README.md
docs/dataset_card.md
docs/provenance.md
docs/ethics.md
docs/faq.md
LICENSES/
```