
# Release Matrix

This document summarizes the public release mode for each subset in the
**Object-Centric Low-Data Datasets** collection.

The collection contains three subsets with different provenance and therefore
different release conditions.

## Summary table

| Subset | Source corpus | Release mode | Are cropped image files redistributed here? | What is publicly released in this repository | What users must obtain separately | Reason for this release mode |
|---|---|---|---|---|---|---|
| Traffic Signs | Author-created dataset | Direct release | Yes | Images, annotations, masks, splits, metadata, checksums, loaders, examples | Nothing upstream required | This subset is owned by the authors and can be released directly |
| Cityscapes--Pedestrian | Cityscapes-derived subset | Abstract / non-image release | No | Documentation, split files, manifests, metadata, code, and carefully limited derived artifacts such as annotations where appropriate | Upstream Cityscapes access by the user | Cityscapes terms do not allow redistribution of the dataset or modified versions such as cropped images |
| COCO PottedPlant | MS-COCO-derived subset | Metadata / reconstruction-first release | Not by default | Annotations, manifests, split files, metadata, code, loaders, and reconstruction tooling | Upstream COCO images by the user | COCO annotations are open, but image rights follow the underlying Flickr terms and are not blanket-safe for bulk redistribution |

## Interpretation

### Traffic Signs
This subset is the fully open anchor subset of the collection. The repository is
intended to host the directly released dataset files together with the
supporting metadata and tooling.

### Cityscapes--Pedestrian
This subset is distributed as a **non-image benchmark overlay**. The repository
does **not** redistribute cropped pedestrian image files. Instead, it provides
the release assets needed to describe and use the subset in a reproducible way,
including metadata, split definitions, manifests, and preparation / loader code.

### COCO PottedPlant
This subset is distributed as a **metadata / reconstruction-first benchmark
overlay**. The repository does **not** assume blanket rights to redistribute the
cropped image subset. Instead, it provides the annotations, manifests, split
files, metadata, and code required to work with the subset once the user has
obtained the upstream images under the original terms.

## Notes on licensing

- **Traffic Signs:** released directly by the authors.
- **Cityscapes--Pedestrian:** follows upstream Cityscapes restrictions; image
  crops are not redistributed here.
- **COCO PottedPlant:** annotations and metadata may be released, but image
  rights remain tied to the original Flickr-sourced images.

See also:

- `LICENSES/traffic_signs_license.txt`
- `LICENSES/cityscapes_notice.txt`
- `LICENSES/coco_notice.txt`
- `docs/dataset_card.md`

