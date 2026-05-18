
"""
COCO PottedPlant reconstruction / preparation entry point.

This script documents and optionally orchestrates the reconstruction pipeline
for the COCO PottedPlant subset.

The subset is not assumed to be redistributed here as a blanket packaged image
release. Instead, this repository provides the code, metadata, and documentation
needed for a user to reconstruct the derived subset locally from the upstream
COCO resources.

Pipeline order:
1. scripts/01_extract_pottedplant_from_coco_to_yolo.py
2. scripts/02_create_instance_crops_from_yolo_pottedplant.py
3. scripts/03_draw_cropped_yolo_bb_debug.py

Important:
- Users must separately obtain the official COCO data.
- Users must comply with the upstream terms that apply to the source files.
- This script does not itself grant rights to the underlying upstream images.
"""

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    subset_root = repo_root / "coco_pottedplant"
    scripts_dir = subset_root / "scripts"
    config_path = subset_root / "metadata" / "pipeline_config_coco.json"

    print("COCO PottedPlant reconstruction entry point")
    print("Repository root:", repo_root)
    print("Subset root:", subset_root)
    print("Scripts directory:", scripts_dir)
    print("Pipeline config:", config_path)
    print("")

    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)

        print("Loaded pipeline configuration:")
        print("  subset_name:", config.get("subset_name"))
        print("  public_standardized_class_name:", config.get("public_standardized_class_name"))
        print("  pipeline_order:")
        for step in config.get("pipeline_order", []):
            print("   -", step)
    else:
        print("Warning: pipeline configuration file not found.")
    print("")

    print("This script is an orchestration wrapper.")
    print("By default it only reports the expected pipeline order.")
    print("If you want to actually run the scripts from here,")
    print("set RUN_PIPELINE = True below and make sure the local COCO")
    print("data paths inside the stage scripts are correct for your data PC.")
    print("")

    RUN_PIPELINE = False

    pipeline = [
        scripts_dir / "01_extract_pottedplant_from_coco_to_yolo.py",
        scripts_dir / "02_create_instance_crops_from_yolo_pottedplant.py",
        scripts_dir / "03_draw_cropped_yolo_bb_debug.py",
    ]

    if not RUN_PIPELINE:
        print("RUN_PIPELINE is False. No scripts were executed.")
        print("Expected execution order:")
        for script in pipeline:
            print(" -", script.name)
        return

    for script in pipeline:
        if not script.exists():
            raise FileNotFoundError(f"Missing pipeline script: {script}")

        print("")
        print(f"Running: {script.name}")
        subprocess.run([sys.executable, str(script)], check=True)

    print("")
    print("Pipeline finished.")


if __name__ == "__main__":
    main()