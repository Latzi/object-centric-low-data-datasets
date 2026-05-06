# TrafficSigns Images

This folder documents the image layout for the **TrafficSigns** subset.

## Important

This folder is **not** the canonical storage location for the released TrafficSigns images.

The actual released image files are stored under the YOLO-style dataset structure in:

- `../Train_Data/images/train/`
- `../Train_Data/images/val/`
- `../Train_Data/test/images/`

## Released image format

The released TrafficSigns images are final object-centric crop images with target size:

- `256×256`

Each released image should have a matching YOLO label file with the same base filename in the corresponding labels folder.

Examples:

- image: `../Train_Data/images/train/2022-04-07T06.03.45.frame1_183_86_2.jpg`
- label: `../Train_Data/labels/train/2022-04-07T06.03.45.frame1_183_86_2.txt`

## Notes

- The authoritative dataset split is defined by the directory structure under `../Train_Data/` and documented in `../splits/README.md`.
- The dataset configuration for YOLO training is provided in `../data.yaml`.
- The metadata manifest for released images is stored in `../metadata/traffic_signs_manifest.csv`.