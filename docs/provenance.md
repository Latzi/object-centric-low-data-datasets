# Provenance: Object-Centric Low-Data Datasets

This document records the provenance and processing history for the **Object-Centric Low-Data Datasets** collection.

The collection contains three subsets:

1. `TrafficSigns`
2. `Cityscapes--Pedestrian`
3. `COCO PottedPlant`

The purpose of this document is to make clear:

- where each subset comes from
- how it was processed
- what is released publicly
- what must be reconstructed locally
- what upstream data or permissions are required
- which public annotation artifacts are included

---

## 1. Summary

| Subset | Source | Release mode | Public image files included? | Public annotation table? |
|---|---|---|---:|---:|
| TrafficSigns | Author-created traffic-sign data | Direct release | Yes | YOLO labels included directly |
| Cityscapes--Pedestrian | Cityscapes-derived | Abstract / non-image release | No | Yes |
| COCO PottedPlant | MS-COCO-derived | Metadata / reconstruction-first release | No blanket image release | Yes |

---

## 2. TrafficSigns provenance

### Source

`TrafficSigns` is an author-created subset used as the cleanest visual regime in the collection.

It is released directly because it does not inherit the same upstream redistribution constraints as the Cityscapes- and COCO-derived subsets.

### Processing

The released subset is stored in YOLO-compatible form under:

```text
traffic_signs/Train_Data/
```

The current structure is:

```text
Train_Data/
    images/
        train/
        val/
    labels/
        train/
        val/
    test/
        images/
        labels/
```

### Public artifacts

The public release includes:

- image files
- YOLO label files
- train / validation / test split structure
- manifest CSV
- summary JSON
- checksum file
- loader script
- loading example
- validation example

### Class mapping

```text
0 -> TrafficSigns
```

### Current metadata

```text
traffic_signs/metadata/traffic_signs_manifest.csv
traffic_signs/metadata/traffic_signs_summary.json
traffic_signs/checksums/traffic_signs_sha256.txt
```

### Current counts

| Split | Count |
|---|---:|
| train | 2256 |
| val | 451 |
| test | 302 |
| total | 3009 |

---

## 3. Cityscapes--Pedestrian provenance

### Source

`Cityscapes--Pedestrian` is derived from upstream Cityscapes data.

The local reconstruction pipeline expects access to Cityscapes folders such as:

```text
leftImg8bit_blurred/
gtBboxCityPersons/
gtCoarse/
```

Users must obtain the Cityscapes data separately and comply with the upstream Cityscapes terms.

This repository does **not** redistribute:

- original Cityscapes images
- derived cropped Cityscapes pedestrian images
- thumbnails or preview images derived from Cityscapes
- mask images derived from Cityscapes crops
- any image-derived artifact intended to substitute for the Cityscapes image subset

### Processing chain

The Cityscapes pipeline is documented through the scripts in:

```text
cityscapes_pedestrian/scripts/
```

The current pipeline order is:

```text
01_create_crops_from_cityscapes_with_bb.py
02_filter_cropped_images.py
03_create_yolo_annotations_from_filtered.py
04_draw_yolo_bb_debug.py
05_create_yolo_split_structure.py
06_build_public_manifest_from_local_yolo.py
```

### Stage 01: crop generation

The first stage starts from the local Cityscapes data and annotation folders.

It performs operations including:

- reading blurred Cityscapes images
- reading CityPersons bounding-box annotations
- reading gtCoarse annotations
- converting polygons to bounding boxes where needed
- merging CityPersons and gtCoarse annotation sources
- removing likely duplicate cross-source objects
- generating candidate `256x256` object-centric crops
- writing cropped intermediate images and COCO-style annotations locally

The public repository includes the script, but not the generated cropped images.

### Stage 02: filtering / difficulty selection

The second stage filters the cropped intermediate subset.

It can select examples according to:

- person-related object count
- overlap statistics
- maximum overlap
- overlap-over-smaller-box
- random selection
- highest / lowest object count

This stage provides control over the difficulty and overlap level of the local reconstructed subset.

### Stage 03: YOLO conversion

The third stage converts the filtered intermediate subset into YOLO-compatible format.

It maps person-related labels into a single public class.

Public standardized class mapping:

```text
0 -> pedestrian
```

### Stage 04: bounding-box visualization

The fourth stage is an inspection / QA utility.

It draws bounding boxes on the local YOLO images so the reconstruction can be visually checked.

These debug images are local QA artifacts and are not redistributed publicly.

### Stage 05: local split creation

The fifth stage converts the local flat YOLO output into a training-ready YOLO split structure:

```text
Train_Data/
    images/
        train/
        val/
    labels/
        train/
        val/
    test/
        images/
        labels/
```

This local `Train_Data` output is not included in the public repository.

### Stage 06: public manifest generation

The sixth stage reads the local authorized `Train_Data` output and generates a public non-image manifest.

The generated public manifest is stored in the repository at:

```text
cityscapes_pedestrian/manifests/cityscapes_pedestrian_manifest.csv
```

### Public annotation table

The public per-box annotation table is stored at:

```text
cityscapes_pedestrian/annotations/cityscapes_pedestrian_boxes.csv
```

This table contains one row per pedestrian-related bounding box associated with the public manifest records.

Current annotation-table row count:

```text
17479 boxes
```

The annotation table does **not** contain:

- image pixels
- cropped pedestrian images
- thumbnails
- preview images
- mask images

It supports:

- annotation inspection
- split-level statistics
- bounding-box mask rasterization
- consistency checks against the manifest
- reconstruction workflows for authorized users

### Public artifacts

The public repository provides:

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

### Current public manifest counts

| Split | Count |
|---|---:|
| train | 1509 |
| val | 323 |
| test | 324 |
| total | 2156 |

---

## 4. COCO PottedPlant provenance

### Source

`COCO PottedPlant` is derived from **MS-COCO 2017**.

The local reconstruction pipeline expects the user to obtain the official COCO resources separately, including:

```text
train2017/
val2017/
annotations_trainval2017/
```

This repository does **not** assume blanket redistribution rights for all COCO-derived image files.

Users must comply with the upstream COCO and source-image terms that apply to those files.

This repository does **not** redistribute:

- original MS-COCO image files
- blanket packaged COCO-derived cropped image files
- thumbnails or preview images derived from COCO
- mask images derived from COCO crops
- any image-derived artifact intended to substitute for the COCO image subset

### Processing chain

The COCO pipeline is documented through the scripts in:

```text
coco_pottedplant/scripts/
```

The current pipeline order is:

```text
01_extract_pottedplant_from_coco_to_yolo.py
02_create_instance_crops_from_yolo_pottedplant.py
03_draw_cropped_yolo_bb_debug.py
04_build_public_manifest_from_local_cropped_yolo.py
```

### Stage 01: category extraction

The first stage starts from the official COCO images and annotations.

It extracts the `potted plant` category by category name and writes a YOLO-compatible full-image subset.

Output is produced locally, not as a blanket image release in this repository.

### Stage 02: per-instance crop generation

The second stage creates `256x256` per-instance object-centric crops.

The crop-generation logic includes:

- one crop per selected potted-plant instance
- random crop offset / margin
- small-box filtering
- preservation of contextual variation
- inclusion of all intersecting potted-plant boxes in the cropped labels

The last point is important: if multiple potted plants are visible in a crop, the cropped label file should include all intersecting potted-plant boxes so visible target objects are not left unlabeled.

### Stage 03: bounding-box visualization

The third stage is an inspection / QA utility.

It draws YOLO bounding boxes on the cropped local images so the annotations can be visually checked.

These debug images are local QA artifacts and are not redistributed publicly.

### Stage 04: public manifest generation

The fourth stage reads the local cropped YOLO subset and creates a public non-image manifest.

The generated public manifest is stored in the repository at:

```text
coco_pottedplant/manifests/coco_pottedplant_manifest.csv
```

### Public annotation table

The public per-box annotation table is stored at:

```text
coco_pottedplant/annotations/coco_pottedplant_boxes.csv
```

This table contains one row per potted-plant bounding box in the locally reconstructed cropped YOLO subset.

Current annotation-table row count:

```text
20230 boxes
```

The annotation table does **not** contain:

- image pixels
- cropped COCO images
- thumbnails
- preview images
- mask images

It supports:

- annotation inspection
- split-level statistics
- bounding-box mask rasterization
- consistency checks against the manifest
- reconstruction workflows for users who obtain COCO separately

### Public artifacts

The public repository provides:

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

### Class mapping

```text
0 -> potted_plant
```

### Current public manifest counts

| Split | Count |
|---|---:|
| train | 7380 |
| val | 299 |
| total | 7679 |

---

## 5. Public vs local artifacts

This repository separates **public artifacts** from **local reconstruction outputs**.

### Public artifacts

Public artifacts include:

- directly releasable TrafficSigns image and label files
- scripts
- manifests
- public per-box annotation CSVs
- metadata
- split documentation
- mask-generation documentation
- checksum files
- license notices
- reconstruction wrappers
- loader / validation examples where applicable

For the reconstruction-first subsets, public annotation CSVs are released under each subset's `annotations/` folder. These files provide one row per bounding box and support inspection, statistics, bounding-box mask rasterization, and reconstruction workflows without redistributing image pixels.

### Local reconstruction outputs

Local reconstruction outputs may include:

- upstream source images
- derived crops
- local YOLO datasets
- debug images with bounding boxes
- local training-ready folders
- intermediate image folders

These files may be generated by authorized users on their own machines, but they are not necessarily redistributable through this repository.

---

### Manifest and annotation table roles

For reconstruction-first subsets, manifests and annotation tables have different roles. Manifest CSVs identify sample-level records, split membership, and reconstruction metadata. Annotation CSVs provide one row per bounding box. Exact local reconstruction also depends on the relevant scripts, pipeline configuration, and authorized upstream data.

## 6. Integrity and reproducibility

Each subset includes or is intended to include checksum files.

For direct-release data, checksums may cover actual data files.

For reconstruction-first subsets, checksums cover public non-image artifacts such as:

- manifests
- public annotation CSVs
- metadata
- scripts
- documentation
- reconstruction wrappers
- pipeline configuration files

If a manifest, annotation CSV, script, metadata file, or documentation file changes, the corresponding checksum file should be regenerated.

---

## 7. Maintenance notes

If the processing pipeline changes, the following files should be updated together where relevant:

```text
README.md
docs/dataset_card.md
docs/release_matrix.md
docs/provenance.md
docs/ethics.md
docs/faq.md
traffic_signs/metadata/traffic_signs_summary.json
cityscapes_pedestrian/metadata/cityscapes_pedestrian_summary.json
cityscapes_pedestrian/metadata/pipeline_config_cityscapes.json
cityscapes_pedestrian/annotations/cityscapes_pedestrian_boxes.csv
coco_pottedplant/metadata/coco_pottedplant_summary.json
coco_pottedplant/metadata/pipeline_config_coco.json
coco_pottedplant/annotations/coco_pottedplant_boxes.csv
```

If manifests or annotation CSVs are regenerated, checksum files should also be regenerated.