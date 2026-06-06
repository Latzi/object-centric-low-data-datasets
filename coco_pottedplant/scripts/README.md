# COCO PottedPlant Scripts

This folder contains the reconstruction and preparation scripts used for the **COCO PottedPlant** subset.

These scripts require a local copy of **MS-COCO 2017**. This repository does **not** redistribute COCO images. Users must obtain COCO separately and provide their own local dataset paths.

## Dependencies

Install the script dependencies from the repository root:

```powershell
pip install -r coco_pottedplant\scripts\requirements_coco.txt
```

The requirements file includes:

```text
opencv-python
tqdm
```

## Expected local COCO layout

The scripts expect the local COCO root to contain the standard COCO 2017 folders:

```text
COCO_ROOT/
    train2017/
    val2017/
    annotations_trainval2017/
        annotations/
            instances_train2017.json
            instances_val2017.json
```

Users should replace the example paths below with their own local paths.

## Pipeline order

The scripts in this folder are intended to be used in the following order:

1. `01_extract_pottedplant_from_coco_to_yolo.py`
2. `02_create_instance_crops_from_yolo_pottedplant.py`
3. `03_draw_cropped_yolo_bb_debug.py`
4. `04_build_public_manifest_from_local_cropped_yolo.py`

## Running the COCO scripts

### 01 — Extract potted plant from COCO into YOLO full-image format

This stage starts from the official downloadable COCO images and annotations, selects the `potted plant` category, and writes a YOLO-compatible subset while preserving the original COCO train/validation split structure.

Example:

```powershell
python coco_pottedplant\scripts\01_extract_pottedplant_from_coco_to_yolo.py `
  --coco-root D:\Datasets\COCO_Dataset `
  --output-dir D:\Datasets\COCO_Dataset\YOLO_pottedplant
```

The `--coco-root` argument can also be supplied through the `COCO_ROOT` environment variable.

### 02 — Create 256x256 per-instance crops

This stage converts the extracted full-image YOLO subset into an object-centric cropped subset. One crop is generated per selected instance. The crop location uses a random offset where possible so that the object is not always centred. Small boxes can be skipped, and intersecting potted-plant boxes can be retained in the cropped labels.

Example:

```powershell
python coco_pottedplant\scripts\02_create_instance_crops_from_yolo_pottedplant.py `
  --coco-root D:\Datasets\COCO_Dataset
```

By default, this reads from:

```text
COCO_ROOT/YOLO_pottedplant
```

and writes to:

```text
COCO_ROOT/YOLO_pottedplant_cropped
```

The source and output folders can also be set explicitly:

```powershell
python coco_pottedplant\scripts\02_create_instance_crops_from_yolo_pottedplant.py `
  --source-dir D:\Datasets\COCO_Dataset\YOLO_pottedplant `
  --output-dir D:\Datasets\COCO_Dataset\YOLO_pottedplant_cropped
```

### 03 — Draw YOLO bounding boxes for inspection

This stage is an optional debug and inspection utility. It renders YOLO bounding boxes on the cropped images so users can visually check the generated labels.

Example:

```powershell
python coco_pottedplant\scripts\03_draw_cropped_yolo_bb_debug.py `
  --coco-root D:\Datasets\COCO_Dataset
```

By default, this reads from:

```text
COCO_ROOT/YOLO_pottedplant_cropped
```

and writes debug images to:

```text
COCO_ROOT/YOLO_pottedplant_cropped/BB
```

### 04 — Build the public manifest from local cropped YOLO outputs

This stage builds the public manifest CSV from locally generated cropped YOLO outputs. It does not copy or redistribute COCO image files.

Example:

```powershell
python coco_pottedplant\scripts\04_build_public_manifest_from_local_cropped_yolo.py `
  --local-cropped-root D:\Datasets\COCO_Dataset\YOLO_pottedplant_cropped `
  --local-full-yolo-root D:\Datasets\COCO_Dataset\YOLO_pottedplant `
  --output-manifest-path coco_pottedplant\manifests\coco_pottedplant_manifest.csv
```

The manifest contains one row per public sample record. The annotation CSV contains one row per potted-plant bounding box.

## Environment variables

The scripts also support environment variables for common local paths:

```text
COCO_ROOT
COCO_CROPPED_YOLO_ROOT
COCO_BB_DEBUG_ROOT
COCO_LOCAL_CROPPED_ROOT
COCO_LOCAL_FULL_YOLO_ROOT
COCO_OUTPUT_MANIFEST_PATH
```

Command-line arguments take precedence when provided.

## Important notes

These scripts are part of the reconstruction and preparation layer for the COCO-derived subset.

This repository does not assume blanket redistribution rights for all COCO-derived image files. Users must obtain the upstream COCO data separately and comply with the original terms that apply to those files.

The public repository releases scripts, manifests, annotation tables, metadata, checksums, and documentation. It does not redistribute the original COCO images or a blanket package of COCO-derived cropped images.

## Related files

See also:

```text
../README.md
../manifests/
../annotations/
../metadata/
../checksums/
../../LICENSES/coco_notice.txt
```