# Tools

This folder contains lightweight utilities for inspecting and preparing public release artifacts.

## Matched manifest subset sampling

`create_matched_manifest_subset.py` creates deterministic matched-size subsets from public manifest CSV files.

This is useful for fixed-budget experiments where users want the same number of records from multiple datasets.

Example:

```powershell
python tools\create_matched_manifest_subset.py `
  --seed 42 `
  --n 2156 `
  --stratify-by-split `
  --output-dir matched_manifests\seed42_n2156 `
  --inputs `
    cityscapes=cityscapes_pedestrian\manifests\cityscapes_pedestrian_manifest.csv `
    traffic=traffic_signs\metadata\traffic_signs_manifest.csv `
    coco=coco_pottedplant\manifests\coco_pottedplant_manifest.csv
```

For training-only matched subsets, use a split filter:

```powershell
python tools\create_matched_manifest_subset.py `
  --seed 42 `
  --n 1509 `
  --split train `
  --output-dir matched_manifests\seed42_train_n1509 `
  --inputs `
    cityscapes=cityscapes_pedestrian\manifests\cityscapes_pedestrian_manifest.csv `
    traffic=traffic_signs\metadata\traffic_signs_manifest.csv `
    coco=coco_pottedplant\manifests\coco_pottedplant_manifest.csv
```

The generated files include:

- one sampled manifest per input dataset
- `matched_manifest_summary.json`
- `README.md`

The sampling is deterministic for a fixed seed.
