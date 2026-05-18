# Dataset Card: Object-Centric Low-Data Datasets

## 1. Overview

This repository contains the public release assets for the **Object-Centric Low-Data Datasets** collection.

The collection contains three object-centric subsets designed for low-data image generation and augmentation research:

1. **TrafficSigns**
2. **Cityscapes--Pedestrian**
3. **COCO PottedPlant**

The three subsets are designed to represent complementary visual regimes:

- **TrafficSigns:** cleaner, sparse, high-contrast object-centric crops
- **Cityscapes--Pedestrian:** dense, occlusion-heavy urban pedestrian scenes with privacy blur
- **COCO PottedPlant:** diverse indoor/outdoor object-centric scenes with contextual variability

The release is intentionally **mixed-mode** because the three subsets have different provenance and redistribution conditions.

## 2. Release modes

| Subset | Release mode | Public image files included? | Main public artifacts |
|---|---|---:|---|
| TrafficSigns | Direct release | Yes | Images, YOLO labels, metadata, manifest, checksums, loaders, examples |
| Cityscapes--Pedestrian | Abstract / non-image release | No | Scripts, manifest, metadata, split documentation, checksums |
| COCO PottedPlant | Metadata / reconstruction-first release | No blanket image release | Scripts, manifest, metadata, split documentation, checksums |

## 3. TrafficSigns

### Summary

**TrafficSigns** is the directly released subset in this collection. It contains final object-centric crop images and YOLO-format annotations.

This subset is intended to provide a clean, lower-complexity regime for object-centric generation and augmentation experiments.

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
    metadata/
    checksums/
    annotations/
    splits/