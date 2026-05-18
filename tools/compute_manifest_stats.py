from __future__ import annotations

from collections import Counter
from pathlib import Path
import csv


REPO_ROOT = Path(__file__).resolve().parents[1]

MANIFESTS = [
    (
        "Cityscapes--Pedestrian",
        REPO_ROOT / "cityscapes_pedestrian" / "manifests" / "cityscapes_pedestrian_manifest.csv",
    ),
    (
        "TrafficSigns",
        REPO_ROOT / "traffic_signs" / "metadata" / "traffic_signs_manifest.csv",
    ),
    (
        "COCO PottedPlant",
        REPO_ROOT / "coco_pottedplant" / "manifests" / "coco_pottedplant_manifest.csv",
    ),
]


def to_int(value) -> int:
    if value is None:
        return 0

    text = str(value).strip()
    if text == "":
        return 0

    try:
        return int(float(text))
    except ValueError:
        return 0


def read_manifest(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    print("Manifest-derived regime statistics")
    print("=" * 40)
    print("")

    latex_rows = []

    for dataset_name, manifest_path in MANIFESTS:
        rows = read_manifest(manifest_path)

        box_counts = [to_int(row.get("num_boxes")) for row in rows]
        record_count = len(rows)
        total_boxes = sum(box_counts)
        mean_boxes = total_boxes / record_count if record_count else 0.0
        multi_box_count = sum(1 for x in box_counts if x > 1)
        multi_box_pct = 100.0 * multi_box_count / record_count if record_count else 0.0
        zero_box_count = sum(1 for x in box_counts if x == 0)
        max_boxes = max(box_counts) if box_counts else 0

        split_counts = Counter(str(row.get("split", "")).strip() for row in rows)

        print(dataset_name)
        print("-" * len(dataset_name))
        print(f"Manifest: {manifest_path}")
        print(f"Records: {record_count:,}")
        print(f"Total boxes: {total_boxes:,}")
        print(f"Mean boxes/record: {mean_boxes:.2f}")
        print(f"Multi-box records: {multi_box_count:,} ({multi_box_pct:.1f}%)")
        print(f"Zero-box records: {zero_box_count:,}")
        print(f"Max boxes in one record: {max_boxes}")
        print("Split counts:", dict(split_counts))
        print("")

        latex_rows.append(
            f"{dataset_name} & {record_count:,} & {mean_boxes:.2f} & {multi_box_pct:.1f}\\% \\\\"
        )

    print("LaTeX table rows")
    print("=" * 40)
    for row in latex_rows:
        print(row)


if __name__ == "__main__":
    main()