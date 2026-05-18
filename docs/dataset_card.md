# Dataset Card: Object-Centric Low-Data Datasets

## 1. Overview

This repository contains the public release assets for the **Object-Centric Low-Data Datasets** collection.

The collection contains three object-centric subsets designed for low-data image generation and augmentation research:

1. **TrafficSigns**
2. **Cityscapes--Pedestrian**
3. **COCO PottedPlant**

The three subsets represent complementary visual regimes:

- **TrafficSigns:** cleaner, sparse, high-contrast object-centric crops
- **Cityscapes--Pedestrian:** dense, occlusion-heavy urban pedestrian scenes with privacy blur
- **COCO PottedPlant:** diverse indoor/outdoor object-centric scenes with contextual variability

The release is intentionally **mixed-mode** because the three subsets have different provenance and redistribution conditions.

Some files are directly released, while other subsets are provided as metadata / reconstruction packages so that users can reproduce them locally from the original upstream datasets.

---

## 2. Release modes

| Subset | Release mode | Public image files included? | Main public artifacts |
|---|---|---:|---|
| TrafficSigns | Direct release | Yes | Images, YOLO labels, manifest, metadata, checksums, loaders, examples |
| Cityscapes--Pedestrian | Abstract / non-image release | No | Scripts, manifest, metadata, split documentation, checksums |
| COCO PottedPlant | Metadata / reconstruction-first release | No blanket image release | Scripts, manifest, metadata, split documentation, checksums |

### Meaning of release modes

**Direct release** means that the dataset files themselves are included in this repository or associated release archive.

**Abstract / non-image release** means that the repository provides non-image artifacts such as scripts, manifests, metadata, split definitions, and documentation, but does not redistribute upstream-derived images.

**Metadata / reconstruction-first release** means that the repository provides the code and metadata needed to reconstruct the subset locally, while users obtain the upstream source data separately.

---

## 3. TrafficSigns

### Summary

**TrafficSigns** is the directly released subset in this collection. It contains final object-centric crop images and YOLO-format annotations.

This subset provides a clean, lower-complexity regime for low-data object-centric generation and augmentation experiments. Compared with the Cityscapes and COCO subsets, TrafficSigns typically contains clearer object boundaries, lower occlusion, and less background complexity.

### Current public structure

```text
traffic_signs/
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
    annotations/
    checksums/
    metadata/
    splits/
```

### Class mapping

```text
0 -> TrafficSigns
```

### Current metadata

The canonical TrafficSigns metadata files are:

```text
traffic_signs/metadata/traffic_signs_manifest.csv
traffic_signs/metadata/traffic_signs_summary.json
```

The manifest records one row per released image, including:

- sample ID
- image path
- annotation path
- split membership
- class ID
- class name
- number of boxes
- released image size
- annotation format

### Current split counts

The current TrafficSigns release contains:

| Split | Count |
|---|---:|
| train | 2256 |
| val | 451 |
| test | 302 |
| total | 3009 |

### Supporting code

The repository includes:

```text
loaders/traffic_signs.py
examples/load_traffic_signs.py
examples/validate_traffic_signs.py
```

These files provide a lightweight loader and basic validation examples for the TrafficSigns subset.

### Release notes

TrafficSigns is the only subset in the current collection where the image files are directly released as part of the public package.

---

## 4. Cityscapes--Pedestrian

### Summary

**Cityscapes--Pedestrian** is a Cityscapes-derived object-centric subset.

It is constructed from upstream Cityscapes data using a multi-stage preparation pipeline. The local pipeline creates `256x256` pedestrian-focused crops from high-resolution Cityscapes frames. This subset is designed to represent a challenging low-data regime involving dense urban scenes, overlap, occlusion, privacy blur, and complex backgrounds.

Because this subset is derived from Cityscapes, this repository does **not** redistribute:

- original Cityscapes images
- derived Cityscapes crop images
- thumbnails or preview images derived from Cityscapes

Instead, the repository provides reconstruction scripts, manifests, metadata, split documentation, and checksums for the public non-image artifacts.

### Release mode

```text
abstract_non_image
```

### Public artifacts

The public repository provides:

```text
cityscapes_pedestrian/scripts/
cityscapes_pedestrian/manifests/
cityscapes_pedestrian/metadata/
cityscapes_pedestrian/splits/
cityscapes_pedestrian/annotations/
cityscapes_pedestrian/checksums/
cityscapes_pedestrian/reconstruct_cityscapes.py
```

### Pipeline stages

The Cityscapes pipeline is documented through the following scripts:

```text
01_create_crops_from_cityscapes_with_bb.py
02_filter_cropped_images.py
03_create_yolo_annotations_from_filtered.py
04_draw_yolo_bb_debug.py
05_create_yolo_split_structure.py
06_build_public_manifest_from_local_yolo.py
```

The pipeline starts from the official Cityscapes folders and produces a local authorized YOLO-style `Train_Data` structure.

The public repository stores the reconstruction scripts and non-image metadata, not the derived image crops.

### Class mapping

```text
0 -> pedestrian
```

### Current public metadata

The canonical public manifest is:

```text
cityscapes_pedestrian/manifests/cityscapes_pedestrian_manifest.csv
```

The subset summary file is:

```text
cityscapes_pedestrian/metadata/cityscapes_pedestrian_summary.json
```

The pipeline configuration file is:

```text
cityscapes_pedestrian/metadata/pipeline_config_cityscapes.json
```

### Current public manifest counts

| Split | Count |
|---|---:|
| train | 1509 |
| val | 323 |
| test | 324 |
| total | 2156 |

### Notes on reconstruction

Users who want to reconstruct the Cityscapes--Pedestrian subset locally must obtain the upstream Cityscapes data separately and comply with the upstream Cityscapes terms.

The repository provides the reconstruction workflow, but it does not grant rights to redistribute or access the underlying Cityscapes image data.

See:

```text
LICENSES/cityscapes_notice.txt
```

---

## 5. COCO PottedPlant

### Summary

**COCO PottedPlant** is an MS-COCO-derived object-centric subset built from the `potted plant` category.

The local reconstruction pipeline extracts the target category from COCO, converts it to YOLO format, creates `256x256` per-instance crops, and generates cropped YOLO labels. The crop-generation step keeps intersecting potted-plant boxes in the cropped labels so that visible additional plants are not left unlabeled.

Because COCO images inherit upstream Flickr image rights, this repository does **not** assume blanket redistribution rights for the cropped image subset.

### Release mode

```text
metadata_reconstruction_first
```

### Public artifacts

The public repository provides:

```text
coco_pottedplant/scripts/
coco_pottedplant/manifests/
coco_pottedplant/metadata/
coco_pottedplant/splits/
coco_pottedplant/annotations/
coco_pottedplant/checksums/
coco_pottedplant/reconstruct_coco.py
```

### Pipeline stages

The COCO pipeline is documented through the following scripts:

```text
01_extract_pottedplant_from_coco_to_yolo.py
02_create_instance_crops_from_yolo_pottedplant.py
03_draw_cropped_yolo_bb_debug.py
04_build_public_manifest_from_local_cropped_yolo.py
```

The pipeline starts from the official COCO 2017 downloads:

```text
train2017/
val2017/
annotations_trainval2017/
```

and produces a local cropped YOLO subset.

### Class mapping

```text
0 -> potted_plant
```

### Current public metadata

The canonical public manifest is:

```text
coco_pottedplant/manifests/coco_pottedplant_manifest.csv
```

The subset summary file is:

```text
coco_pottedplant/metadata/coco_pottedplant_summary.json
```

The pipeline configuration file is:

```text
coco_pottedplant/metadata/pipeline_config_coco.json
```

### Current public manifest counts

The exact current split counts are stored in:

```text
coco_pottedplant/metadata/coco_pottedplant_summary.json
```

### Notes on reconstruction

Users who want to reconstruct the COCO PottedPlant subset locally must obtain the upstream COCO images and annotations separately and comply with the upstream terms that apply to those files.

The repository provides the reconstruction workflow and metadata, but it does not assume blanket permission to redistribute all COCO-derived cropped images.

See:

```text
LICENSES/coco_notice.txt
```

---

## 6. Common design across subsets

Across the collection, the release aims to provide:

- documented preprocessing pipelines
- machine-readable manifests
- subset-level summary metadata
- split documentation
- checksum files
- reconstruction scripts
- dataset loading / validation examples where appropriate

The goal is to make the datasets reproducible and usable while respecting upstream redistribution constraints.

### Manifest layer

Each subset has or will have a canonical manifest file. These manifests are intended to support:

- reproducibility
- split tracking
- metadata lookup
- integrity checking
- reconstruction workflows

### Metadata layer

Each subset has summary metadata describing:

- release mode
- class mapping
- split counts
- pipeline settings
- source dataset assumptions
- relevant limitations

### Script layer

Each reconstruction-first subset has scripts that document the actual preparation pipeline.

---

## 7. Intended uses

This collection is intended for research on:

- low-data object-centric image generation
- few-shot generative modeling
- synthetic data augmentation
- object-centric representation learning
- generative model evaluation
- reconstruction-aware dataset release workflows
- benchmarking under constrained-data settings

---

## 8. Out-of-scope uses

This collection is not intended for:

- identity recognition
- surveillance
- bypassing upstream dataset terms
- redistributing upstream-restricted image data
- commercial use where upstream terms do not permit it
- replacing the official upstream Cityscapes or COCO datasets

---

## 9. Licensing and redistribution

Licensing differs by subset.

- **TrafficSigns** is directly released by the authors.
- **Cityscapes--Pedestrian** is released as a non-image reconstruction / metadata package.
- **COCO PottedPlant** is released as a metadata / reconstruction-first package.

See:

```text
LICENSES/traffic_signs_license.txt
LICENSES/cityscapes_notice.txt
LICENSES/coco_notice.txt
```

Users are responsible for complying with upstream licenses and terms when reconstructing subsets from Cityscapes or COCO.

---

## 10. Checksums

Checksum files are included to verify public release artifacts.

For the direct-release TrafficSigns subset, checksums may cover dataset files.

For reconstruction-first subsets, checksums cover public non-image artifacts such as:

- scripts
- metadata
- manifests
- documentation
- reconstruction wrappers
- pipeline configuration files

Checksum files do not grant redistribution rights for upstream datasets.

---

## 11. Citation

Citation metadata will be provided in:

```text
CITATION.cff
```

A DOI-backed archival release should be added before or at submission time.

Until then, users should cite the associated paper and the relevant upstream datasets where applicable.