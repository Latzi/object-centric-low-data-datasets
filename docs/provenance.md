\# Provenance: Object-Centric Low-Data Datasets



This document records the provenance and processing history for the \*\*Object-Centric Low-Data Datasets\*\* collection.



The collection contains three subsets:



1\. `TrafficSigns`

2\. `Cityscapes--Pedestrian`

3\. `COCO PottedPlant`



The purpose of this document is to make clear:



\- where each subset comes from

\- how it was processed

\- what is released publicly

\- what must be reconstructed locally

\- what upstream data or permissions are required



\---



\## 1. Summary



| Subset | Source | Release mode | Public image files included? |

|---|---|---|---:|

| TrafficSigns | Author-created traffic-sign data | Direct release | Yes |

| Cityscapes--Pedestrian | Cityscapes-derived | Abstract / non-image release | No |

| COCO PottedPlant | MS-COCO-derived | Metadata / reconstruction-first release | No blanket image release |



\---



\## 2. TrafficSigns provenance



\### Source



`TrafficSigns` is an author-created subset used as the cleanest visual regime in the collection.



It is released directly because it does not inherit the same upstream redistribution constraints as the Cityscapes- and COCO-derived subsets.



\### Processing



The released subset is stored in YOLO-compatible form under:



```text

traffic\_signs/Train\_Data/

```



The current structure is:



```text

Train\_Data/

&#x20;   images/

&#x20;       train/

&#x20;       val/

&#x20;   labels/

&#x20;       train/

&#x20;       val/

&#x20;   test/

&#x20;       images/

&#x20;       labels/

```



\### Public artifacts



The public release includes:



\- image files

\- YOLO label files

\- train / validation / test split structure

\- manifest CSV

\- summary JSON

\- checksum file

\- loader script

\- loading example

\- validation example



\### Class mapping



```text

0 -> TrafficSigns

```



\### Current metadata



```text

traffic\_signs/metadata/traffic\_signs\_manifest.csv

traffic\_signs/metadata/traffic\_signs\_summary.json

traffic\_signs/checksums/traffic\_signs\_sha256.txt

```



\---



\## 3. Cityscapes--Pedestrian provenance



\### Source



`Cityscapes--Pedestrian` is derived from upstream Cityscapes data.



The local reconstruction pipeline expects access to Cityscapes folders such as:



```text

leftImg8bit\_blurred/

gtBboxCityPersons/

gtCoarse/

```



Users must obtain the Cityscapes data separately and comply with the upstream Cityscapes terms.



This repository does \*\*not\*\* redistribute:



\- original Cityscapes images

\- derived cropped Cityscapes pedestrian images

\- thumbnails or preview images derived from Cityscapes



\### Processing chain



The Cityscapes pipeline is documented through the scripts in:



```text

cityscapes\_pedestrian/scripts/

```



The current pipeline order is:



```text

01\_create\_crops\_from\_cityscapes\_with\_bb.py

02\_filter\_cropped\_images.py

03\_create\_yolo\_annotations\_from\_filtered.py

04\_draw\_yolo\_bb\_debug.py

05\_create\_yolo\_split\_structure.py

06\_build\_public\_manifest\_from\_local\_yolo.py

```



\### Stage 01: crop generation



The first stage starts from the local Cityscapes data and annotation folders.



It performs operations including:



\- reading blurred Cityscapes images

\- reading CityPersons bounding-box annotations

\- reading gtCoarse annotations

\- converting polygons to bounding boxes where needed

\- merging CityPersons and gtCoarse annotation sources

\- removing likely duplicate cross-source objects

\- generating candidate `256x256` object-centric crops

\- writing cropped intermediate images and COCO-style annotations locally



The public repository includes the script, but not the generated cropped images.



\### Stage 02: filtering / difficulty selection



The second stage filters the cropped intermediate subset.



It can select examples according to:



\- person-related object count

\- overlap statistics

\- maximum overlap

\- overlap-over-smaller-box

\- random selection

\- highest / lowest object count



This stage provides control over the difficulty and overlap level of the local reconstructed subset.



\### Stage 03: YOLO conversion



The third stage converts the filtered intermediate subset into YOLO-compatible format.



It merges person-related labels into a single public class.



Public standardized class mapping:



```text

0 -> pedestrian

```



\### Stage 04: bounding-box visualization



The fourth stage is an inspection / QA utility.



It draws bounding boxes on the local YOLO images so the reconstruction can be visually checked.



These debug images are local QA artifacts and are not redistributed publicly.



\### Stage 05: local split creation



The fifth stage converts the local flat YOLO output into a training-ready YOLO split structure:



```text

Train\_Data/

&#x20;   images/

&#x20;       train/

&#x20;       val/

&#x20;   labels/

&#x20;       train/

&#x20;       val/

&#x20;   test/

&#x20;       images/

&#x20;       labels/

```



This local `Train\_Data` output is not included in the public repository.



\### Stage 06: public manifest generation



The sixth stage reads the local authorized `Train\_Data` output and generates a public non-image manifest.



The generated public manifest is stored in the repository at:



```text

cityscapes\_pedestrian/manifests/cityscapes\_pedestrian\_manifest.csv

```



\### Public artifacts



The public repository provides:



```text

cityscapes\_pedestrian/scripts/

cityscapes\_pedestrian/reconstruct\_cityscapes.py

cityscapes\_pedestrian/manifests/cityscapes\_pedestrian\_manifest.csv

cityscapes\_pedestrian/metadata/cityscapes\_pedestrian\_summary.json

cityscapes\_pedestrian/metadata/pipeline\_config\_cityscapes.json

cityscapes\_pedestrian/checksums/cityscapes\_pedestrian\_public\_sha256.txt

LICENSES/cityscapes\_notice.txt

```



\### Current public manifest counts



| Split | Count |

|---|---:|

| train | 1509 |

| val | 323 |

| test | 324 |

| total | 2156 |



\---



\## 4. COCO PottedPlant provenance



\### Source



`COCO PottedPlant` is derived from \*\*MS-COCO 2017\*\*.



The local reconstruction pipeline expects the user to obtain the official COCO resources separately, including:



```text

train2017/

val2017/

annotations\_trainval2017/

```



This repository does \*\*not\*\* assume blanket redistribution rights for all COCO-derived image files.



Users must comply with the upstream COCO and source-image terms that apply to those files.



\### Processing chain



The COCO pipeline is documented through the scripts in:



```text

coco\_pottedplant/scripts/

```



The current pipeline order is:



```text

01\_extract\_pottedplant\_from\_coco\_to\_yolo.py

02\_create\_instance\_crops\_from\_yolo\_pottedplant.py

03\_draw\_cropped\_yolo\_bb\_debug.py

04\_build\_public\_manifest\_from\_local\_cropped\_yolo.py

```



\### Stage 01: category extraction



The first stage starts from the official COCO images and annotations.



It extracts the `potted plant` category and writes a YOLO-compatible full-image subset.



Output is produced locally, not as a blanket image release in this repository.



\### Stage 02: per-instance crop generation



The second stage creates `256x256` per-instance object-centric crops.



The crop-generation logic includes:



\- one crop per selected potted-plant instance

\- random crop offset / margin

\- small-box filtering

\- preservation of contextual variation

\- inclusion of all intersecting potted-plant boxes in the cropped labels



The last point is important: if multiple potted plants are visible in a crop, the cropped label file should include all intersecting potted-plant boxes so visible objects are not left unlabeled.



\### Stage 03: bounding-box visualization



The third stage is an inspection / QA utility.



It draws YOLO bounding boxes on the cropped local images so the annotations can be visually checked.



These debug images are local QA artifacts and are not redistributed publicly.



\### Stage 04: public manifest generation



The fourth stage reads the local cropped YOLO subset and creates a public non-image manifest.



The generated public manifest is stored in the repository at:



```text

coco\_pottedplant/manifests/coco\_pottedplant\_manifest.csv

```



\### Public artifacts



The public repository provides:



```text

coco\_pottedplant/scripts/

coco\_pottedplant/reconstruct\_coco.py

coco\_pottedplant/manifests/coco\_pottedplant\_manifest.csv

coco\_pottedplant/metadata/coco\_pottedplant\_summary.json

coco\_pottedplant/metadata/pipeline\_config\_coco.json

coco\_pottedplant/checksums/coco\_pottedplant\_public\_sha256.txt

LICENSES/coco\_notice.txt

```



\### Class mapping



```text

0 -> potted\_plant

```



\---



\## 5. Public vs local artifacts



This repository separates \*\*public artifacts\*\* from \*\*local reconstruction outputs\*\*.



\### Public artifacts



Public artifacts include:



\- scripts

\- manifests

\- metadata

\- split documentation

\- checksum files

\- license notices

\- reconstruction wrappers

\- loader / validation examples where applicable



\### Local reconstruction outputs



Local reconstruction outputs may include:



\- upstream source images

\- derived crops

\- local YOLO datasets

\- debug images with bounding boxes

\- local training-ready folders



These files may be generated by authorized users on their own machines, but they are not necessarily redistributed through this repository.



\---



\## 6. Integrity and reproducibility



Each subset includes or is intended to include checksum files.



For direct-release data, checksums may cover actual data files.



For reconstruction-first subsets, checksums cover public non-image artifacts such as:



\- manifests

\- metadata

\- scripts

\- documentation

\- reconstruction wrappers

\- pipeline configuration files



\---



\## 7. Maintenance notes



If the processing pipeline changes, the following files should be updated together:



```text

docs/dataset\_card.md

docs/release\_matrix.md

docs/provenance.md

traffic\_signs/metadata/traffic\_signs\_summary.json

cityscapes\_pedestrian/metadata/cityscapes\_pedestrian\_summary.json

cityscapes\_pedestrian/metadata/pipeline\_config\_cityscapes.json

coco\_pottedplant/metadata/coco\_pottedplant\_summary.json

coco\_pottedplant/metadata/pipeline\_config\_coco.json

```



If manifests are regenerated, checksum files should also be regenerated.

