from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Iterator, List, Optional


@dataclass
class TrafficSignsRecord:
    sample_id: str
    image_path: Path
    label_path: Optional[Path]
    split: str
    class_id: int
    class_name: str
    num_boxes: int
    released_width: int
    released_height: int
    annotation_format: str
    notes: str


class TrafficSignsDataset:
    """
    Lightweight loader for the TrafficSigns subset.

    This loader reads the canonical metadata manifest and resolves
    the real image and label paths inside the repository.
    """

    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.traffic_root = self.repo_root / "traffic_signs"
        self.manifest_path = self.traffic_root / "metadata" / "traffic_signs_manifest.csv"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

        self.records: List[TrafficSignsRecord] = self._load_manifest()

    def _load_manifest(self) -> List[TrafficSignsRecord]:
        records: List[TrafficSignsRecord] = []

        with self.manifest_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_path = self.traffic_root / row["image_relpath"]

                annotation_rel = row["annotation_relpath"].strip()
                label_path = self.traffic_root / annotation_rel if annotation_rel else None

                record = TrafficSignsRecord(
                    sample_id=row["sample_id"],
                    image_path=image_path,
                    label_path=label_path,
                    split=row["split"],
                    class_id=int(row["class_id"]),
                    class_name=row["class_name"],
                    num_boxes=int(row["num_boxes"]),
                    released_width=int(row["released_width"]),
                    released_height=int(row["released_height"]),
                    annotation_format=row["annotation_format"],
                    notes=row["notes"],
                )
                records.append(record)

        return records

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator[TrafficSignsRecord]:
        return iter(self.records)

    def by_split(self, split: str) -> List[TrafficSignsRecord]:
        return [r for r in self.records if r.split == split]

    def summary(self) -> dict:
        split_counts = {}
        for r in self.records:
            split_counts[r.split] = split_counts.get(r.split, 0) + 1

        return {
            "total_records": len(self.records),
            "split_counts": split_counts,
            "manifest_path": str(self.manifest_path),
        }


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    dataset = TrafficSignsDataset(repo_root)

    print("TrafficSigns dataset loaded")
    print(dataset.summary())

    print("\nFirst 5 records:")
    for item in dataset.records[:5]:
        print(
            {
                "sample_id": item.sample_id,
                "split": item.split,
                "image": item.image_path.name,
                "label": item.label_path.name if item.label_path else None,
                "num_boxes": item.num_boxes,
            }
        )