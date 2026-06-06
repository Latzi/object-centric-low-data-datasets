# Cityscapes--Pedestrian Scripts

This folder contains the reconstruction and preparation scripts used for the **Cityscapes--Pedestrian** subset.

These scripts require a local authorized copy of **Cityscapes** and related annotation sources. This repository does **not** redistribute Cityscapes images, cropped Cityscapes-derived images, thumbnails, preview images, or derived mask images. Users must obtain Cityscapes separately and provide their own local dataset paths.

## Dependencies

Install the script dependencies from the repository root:

```powershell
pip install -r cityscapes_pedestrian\scripts\requirements_cityscapes.txt
```

The requirements file includes:

```text
opencv-python
tqdm
```

## Expected local Cityscapes layout

The scripts expect the local Cityscapes root to contain the required image and annotation folders.

Expected structure:

```text
CITYSCAPES_ROOT/
    leftImg8bit_blurred/
        leftImg8bit_blurred/
            train/
            val/
    gtBbox_cityPersons_trainval/
        gtBboxCityPersons/
            train/
            val/
    gtCoarse/
        gtCoarse/
            train/
            val/
```

Users should replace the example paths below with their own local paths.

## Pipeline order

The scripts in this folder are intended to be used in the following order:

1. `01_create_crops_from_cityscapes_with_bb.py`
2. `02_filter_cropped_images.py`
3. `03_create_yolo_annotations_from_filtered.py`
4. `04_draw_yolo_bb_debug.py`
5. `05_create_yolo_split_structure.py`
6. `06_build_public_manifest_from_local_yolo.py`

## Running the Cityscapes scripts

### 01 — Create crops from original Cityscapes sources

This stage starts from an authorized local Cityscapes copy and related annotation sources. It merges relevant person-related categories, removes likely duplicate cross-source objects, generates candidate `256x256` crops, and exports an intermediate cropped dataset plus COCO-style annotations.

Example:

```powershell
python cityscapes_pedestrian\scripts\01_create_crops_from_cityscapes_with_bb.py `
  --cityscapes-root D:\Datasets\Cityscapes
```

The `--cityscapes-root` argument can also be supplied through the `CITYSCAPES_ROOT` environment variable.

Optional explicit paths can also be supplied:

```powershell
python cityscapes_pedestrian\scripts\01_create_crops_from_cityscapes_with_bb.py `
  --images-dir D:\Datasets\Cityscapes\leftImg8bit_blurred\leftImg8bit_blurred `
  --bbox-dir D:\Datasets\Cityscapes\gtBbox_cityPersons_trainval\gtBboxCityPersons `
  --coarse-dir D:\Datasets\Cityscapes\gtCoarse\gtCoarse `
  --output-dir D:\Datasets\Cityscapes\processed
```

### 02 — Filter cropped images

This stage applies subset-selection logic to the cropped intermediate dataset. It supports filtering by object counts and overlap statistics, allowing the user to control difficulty and final subset composition.

Example:

```powershell
python cityscapes_pedestrian\scripts\02_filter_cropped_images.py `
  --processed-dir D:\Datasets\Cityscapes\processed
```

By default, this reads:

```text
PROCESSED_DIR/cropped_images
PROCESSED_DIR/cropped_annotations.json
```

and writes:

```text
PROCESSED_DIR/filtered_images
```

Optional explicit paths can also be supplied:

```powershell
python cityscapes_pedestrian\scripts\02_filter_cropped_images.py `
  --images-dir D:\Datasets\Cityscapes\processed\cropped_images `
  --annotations-file D:\Datasets\Cityscapes\processed\cropped_annotations.json `
  --filtered-dir D:\Datasets\Cityscapes\processed\filtered_images
```

### 03 — Convert filtered subset to YOLO format

This stage converts the filtered subset into YOLO-compatible images, labels, class definitions, and dataset configuration files.

Example:

```powershell
python cityscapes_pedestrian\scripts\03_create_yolo_annotations_from_filtered.py `
  --processed-dir D:\Datasets\Cityscapes\processed
```

By default, this reads:

```text
PROCESSED_DIR/filtered_images
PROCESSED_DIR/filtered_images/filtered_annotations.json
```

and writes:

```text
PROCESSED_DIR/filtered_yolo
```

Optional explicit paths can also be supplied:

```powershell
python cityscapes_pedestrian\scripts\03_create_yolo_annotations_from_filtered.py `
  --filtered-images-dir D:\Datasets\Cityscapes\processed\filtered_images `
  --filtered-annotations-file D:\Datasets\Cityscapes\processed\filtered_images\filtered_annotations.json `
  --yolo-output-dir D:\Datasets\Cityscapes\processed\filtered_yolo
```

### 04 — Draw YOLO bounding boxes for inspection

This stage is an optional debug and inspection utility. It renders YOLO bounding boxes on images for visual verification.

Example:

```powershell
python cityscapes_pedestrian\scripts\04_draw_yolo_bb_debug.py `
  --processed-dir D:\Datasets\Cityscapes\processed
```

By default, this reads:

```text
PROCESSED_DIR/filtered_yolo
```

and writes debug images to:

```text
PROCESSED_DIR/filtered_yolo/BB
```

Optional explicit paths can also be supplied:

```powershell
python cityscapes_pedestrian\scripts\04_draw_yolo_bb_debug.py `
  --yolo-dir D:\Datasets\Cityscapes\processed\filtered_yolo `
  --bb-output-dir D:\Datasets\Cityscapes\processed\filtered_yolo\BB
```

### 05 — Create local YOLO train/validation/test split structure

This stage creates a local YOLO-compatible `Train_Data` folder from the filtered YOLO output.

Example:

```powershell
python cityscapes_pedestrian\scripts\05_create_yolo_split_structure.py `
  --processed-dir D:\Datasets\Cityscapes\processed
```

By default, this reads:

```text
PROCESSED_DIR/filtered_yolo
```

and writes:

```text
PROCESSED_DIR/Train_Data
```

Optional explicit paths can also be supplied:

```powershell
python cityscapes_pedestrian\scripts\05_create_yolo_split_structure.py `
  --source-yolo-dir D:\Datasets\Cityscapes\processed\filtered_yolo `
  --output-dir D:\Datasets\Cityscapes\processed\Train_Data
```

### 06 — Build the public manifest from local YOLO outputs

This stage builds the public Cityscapes--Pedestrian manifest CSV from a local authorized YOLO `Train_Data` folder. It does not copy or redistribute Cityscapes image files.

Example:

```powershell
python cityscapes_pedestrian\scripts\06_build_public_manifest_from_local_yolo.py `
  --local-dataset-root D:\Datasets\Cityscapes\processed\Train_Data `
  --output-manifest-path cityscapes_pedestrian\manifests\cityscapes_pedestrian_manifest.csv
```

The manifest contains one row per public sample record. The annotation CSV contains one row per pedestrian-related bounding box.

## Environment variables

The scripts also support environment variables for common local paths:

```text
CITYSCAPES_ROOT
CITYSCAPES_PROCESSED_DIR
CITYSCAPES_FILTERED_DIR
CITYSCAPES_FILTERED_YOLO_DIR
CITYSCAPES_BB_DEBUG_DIR
CITYSCAPES_TRAIN_DATA_DIR
CITYSCAPES_LOCAL_YOLO_ROOT
CITYSCAPES_OUTPUT_MANIFEST_PATH
```

Command-line arguments take precedence when provided.

## Important notes

These scripts are part of the reconstruction and preparation layer for the Cityscapes-derived subset.

This repository does not redistribute Cityscapes images, cropped Cityscapes pedestrian images, thumbnails, preview images, or derived mask images. Users must obtain Cityscapes separately and comply with the upstream Cityscapes terms.

The public repository releases scripts, manifests, annotation tables, metadata, checksums, and documentation. It does not redistribute Cityscapes image data.

## Related files

See also:

```text
../README.md
../manifests/
../annotations/
../metadata/
../checksums/
../../LICENSES/cityscapes_notice.txt
```