from pathlib import Path

from loaders.traffic_signs import TrafficSignsDataset


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    dataset = TrafficSignsDataset(repo_root)

    print("TrafficSigns dataset loaded successfully")
    print(dataset.summary())

    print("\nFirst 5 records:")
    for item in dataset.records[:5]:
        print(
            {
                "sample_id": item.sample_id,
                "split": item.split,
                "image": str(item.image_path),
                "label": str(item.label_path) if item.label_path else None,
                "num_boxes": item.num_boxes,
            }
        )


if __name__ == "__main__":
    main()