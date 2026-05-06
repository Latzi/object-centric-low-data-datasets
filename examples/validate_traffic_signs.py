from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from loaders.traffic_signs import TrafficSignsDataset


def main() -> None:
    dataset = TrafficSignsDataset(REPO_ROOT)

    missing_images = []
    missing_labels = []
    bad_box_counts = []

    for item in dataset.records:
        if not item.image_path.exists():
            missing_images.append(item.sample_id)

        if item.label_path is None or not item.label_path.exists():
            missing_labels.append(item.sample_id)
            continue

        with item.label_path.open("r", encoding="utf-8") as f:
            num_lines = sum(1 for line in f if line.strip())

        if num_lines != item.num_boxes:
            bad_box_counts.append((item.sample_id, item.num_boxes, num_lines))

    print("TrafficSigns validation report")
    print(f"Total records: {len(dataset.records)}")
    print(f"Missing images: {len(missing_images)}")
    print(f"Missing labels: {len(missing_labels)}")
    print(f"Box-count mismatches: {len(bad_box_counts)}")

    if missing_images:
        print("\nFirst missing images:")
        for x in missing_images[:10]:
            print(x)

    if missing_labels:
        print("\nFirst missing labels:")
        for x in missing_labels[:10]:
            print(x)

    if bad_box_counts:
        print("\nFirst box-count mismatches:")
        for x in bad_box_counts[:10]:
            print(x)

    if not missing_images and not missing_labels and not bad_box_counts:
        print("\nAll checks passed.")


if __name__ == "__main__":
    main()