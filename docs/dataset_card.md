# Dataset Card: Object-Centric Low-Data Datasets

## 1. Summary

**Object-Centric Low-Data Datasets** is a curated collection of three object-centric subsets designed for low-data image generation and augmentation:

- **Traffic Signs**
- **Cityscapes--Pedestrian**
- **COCO PottedPlant**

The collection was created to support research on object-centric generative modelling under limited-data conditions, especially in settings involving blur, occlusion, sparse object occurrence, or high background variability.

## 2. Motivation

Many modern generative models assume large training corpora. In practice, however, many object-centric domains provide only a few thousand usable samples. Existing image datasets are usually organized for classification, detection, or scene understanding rather than for controlled low-data object-centric generative modelling.

This collection was curated to provide:

- a matched three-subset benchmark for low-data object-centric generation and augmentation,
- a common object-detection / crop-generation pipeline,
- standardized `256×256` object-centric crops,
- aligned bounding-box mask information,
- a release package suitable for reproducible research.

## 3. Collection overview

| Subset | Source | Main regime | Planned release mode |
|---|---|---|---|
| Traffic Signs | Author-created dataset | sparse / visually clean / low occlusion | direct release |
| Cityscapes--Pedestrian | derived from Cityscapes | dense / occlusion-heavy / privacy blur | abstract / non-image release |
| COCO PottedPlant | derived from MS-COCO | context-diverse / indoor-outdoor / variable placement | metadata / reconstruction-first release |

## 4. Data composition

The collection contains three small object-centric subsets, each designed for low-data experiments.

Common properties across subsets:

- target format: `256×256`
- object-centric crops
- bounding-box-based curation
- aligned binary bounding-box masks
- low-data regime (each subset contains fewer than 3k samples in the FDGAN setup)

The three subsets cover complementary visual conditions:

- **Cityscapes--Pedestrian:** dense scenes, overlap, occlusion, privacy-blurred faces
- **Traffic Signs:** simpler scenes, sharp object boundaries, low clutter
- **COCO PottedPlant:** diverse indoor/outdoor contexts, variable object placement, wider background diversity

## 5. Source data and curation process

### 5.1 Traffic Signs
This subset is built from an author-created traffic-sign dataset. The target classes are merged into a single traffic-sign category, and sign-centered crops are generated with randomized object positioning inside the crop.

### 5.2 Cityscapes--Pedestrian
This subset is derived from the Cityscapes dataset. The classes `person`, `rider`, `group`, and `sitting person` are merged into a unified pedestrian category. Bounding boxes are obtained using a pretrained YOLOv5x detector, and each accepted detection is cropped into a `256×256` patch with randomized offset.

### 5.3 COCO PottedPlant
This subset is derived from MS-COCO 2017 by selecting the `potted plant` category. Crops are generated per annotated instance so that the object bounding box remains inside the `256×256` crop, with random margin and varying surrounding context.

## 6. Construction pipeline

The collection follows a common curation workflow:

1. object detection or annotation lookup  
2. bounding-box extraction  
3. object-centric crop generation  
4. normalization to `256×256`  
5. filtering of invalid or low-quality crops  
6. aligned mask creation and metadata packaging

For the FDGAN setting, this common pipeline is one of the core contributions of the resource.

## 7. Release contents

This repository uses a mixed release model.

### Traffic Signs
Planned direct-release contents:

- images
- annotations
- masks
- split files
- metadata
- checksums
- loaders / examples

### Cityscapes--Pedestrian
Planned non-image release contents:

- annotations
- split files
- manifests
- metadata
- checksums
- reconstruction / preparation scripts
- loaders / examples

### COCO PottedPlant
Planned metadata / reconstruction-first contents:

- annotations
- split files
- manifests
- metadata
- checksums
- reconstruction / preparation scripts
- loaders / examples

## 8. Intended uses

This collection is intended for research on:

- object-centric image generation
- low-data generative modelling
- few-shot generative learning
- data augmentation
- generative model evaluation
- object-level representation learning

## 9. Out-of-scope uses

This resource is **not** intended for:

- identity recognition
- surveillance applications
- use that overrides upstream dataset terms
- redistribution of upstream image data where such redistribution is not permitted

## 10. Limitations

Users should be aware of the following limitations:

- the collection is intentionally small and designed for low-data settings
- the three subsets differ in source provenance and release conditions
- Cityscapes- and COCO-derived subsets inherit upstream access and licensing constraints
- exact released artifacts may differ by subset because not all image files can be redistributed in the same way
- the collection is curated for object-centric generative research and is not a general-purpose vision benchmark

## 11. Licensing and redistribution

Licensing differs by subset.

- **Traffic Signs:** direct release by the authors
- **Cityscapes--Pedestrian:** cropped images are not redistributed here; release is limited to abstract / non-image assets
- **COCO PottedPlant:** annotations and metadata may be released here, but image redistribution is constrained by upstream rights

See:

- `LICENSES/traffic_signs_license.txt`
- `LICENSES/cityscapes_notice.txt`
- `LICENSES/coco_notice.txt`

## 12. Ethics and privacy

The collection includes a pedestrian subset derived from real-world urban scenes. This subset preserves the privacy protections already present in the source imagery, including blurred faces.

Users should consult the provenance and licensing notices before using the collection in downstream applications.

Additional ethics notes are provided in:

- `docs/ethics.md`
- `docs/provenance.md`

## 13. Versioning and maintenance

This repository is versioned as a research artifact. Release notes and archival information will be provided alongside DOI-backed releases.

Planned archival metadata will be stored in:

- `zenodo/deposition_metadata.json`
- `zenodo/release_notes.md`

## 14. Citation

Citation metadata will be provided in:

- `CITATION.cff`

A DOI-backed archival release will be added when the first stable public version is prepared.

## 15. Contact

Repository contact details will be added here in a later update.
