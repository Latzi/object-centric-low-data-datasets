"""
Reconstruction / preparation placeholder for the Cityscapes--Pedestrian subset.

This subset is released in abstract / non-image form. The purpose of this script
is to document the intended reconstruction flow for authorized users who have
separately obtained access to the original Cityscapes dataset under the upstream
terms.

Intended high-level workflow:
1. Load the authorized upstream Cityscapes images and annotations.
2. Select pedestrian-related classes:
   - person
   - rider
   - group
   - sitting person
3. Merge those classes into a unified pedestrian category.
4. Obtain bounding boxes using the chosen preparation method
   (for example, the YOLOv5x-based workflow described in the paper/supplement).
5. Apply the size rule used for the subset (minimum object size rule).
6. Define 256x256 crop windows around accepted detections.
7. Record non-image release artifacts such as:
   - sample identifiers
   - source image identifiers
   - split assignments
   - box-size metadata
   - derived artifact references
8. Export public non-image artifacts for this repository, such as:
   - manifests
   - metadata
   - split definitions
   - annotation tables

Important:
- This script is a documented placeholder and does not redistribute Cityscapes
  image data.
- Users must separately obtain access to the original Cityscapes dataset and
  comply with the official upstream terms.
- Any future implementation of this script should preserve the repository's
  abstract / non-image release model.

See also:
- cityscapes_pedestrian/README.md
- cityscapes_pedestrian/manifests/
- cityscapes_pedestrian/metadata/
- LICENSES/cityscapes_notice.txt
"""

from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    print("Cityscapes--Pedestrian reconstruction placeholder")
    print("Repository root:", repo_root)
    print("")
    print("This script is currently a documented placeholder.")
    print("It does not reconstruct or export Cityscapes image data.")
    print("Use it as the starting point for an authorized internal")
    print("preparation workflow that generates only the permitted")
    print("non-image release artifacts for this repository.")


if __name__ == "__main__":
    main()
