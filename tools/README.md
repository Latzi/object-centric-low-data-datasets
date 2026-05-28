# Tools

This folder contains lightweight utilities for inspecting and preparing public release artifacts.

## Matched manifest subset sampling

`create_matched_manifest_subset.py` creates deterministic matched-size subsets from public manifest CSV files.

This is useful for fixed-budget experiments where users want the same number of records from multiple datasets.

### Example: matched subsets across all splits

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

### Example: training-only matched subsets

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

### Outputs

The generated files include:

- one sampled manifest per input dataset
- `matched_manifest_summary.json`
- `README.md`

The sampling is deterministic for a fixed seed.

## Checksum verification

`verify_release_checksums.py` verifies the subset-level SHA256 checksum files included in the public release.

Run from the repository root:

```powershell
python tools\verify_release_checksums.py
```

The tool checks:

- `traffic_signs/checksums/traffic_signs_sha256.txt`
- `cityscapes_pedestrian/checksums/cityscapes_pedestrian_public_sha256.txt`
- `coco_pottedplant/checksums/coco_pottedplant_public_sha256.txt`

A successful run reports:

```text
Checksum verification PASSED.
```

## Notes

These tools operate on public release artifacts.

They do not download upstream datasets and they do not grant rights to Cityscapes or COCO image data.