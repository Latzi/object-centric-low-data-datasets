# FAQ

This document answers common questions about the **Object-Centric Low-Data Datasets** collection.

The collection contains three subsets:

1. `TrafficSigns`
2. `Cityscapes--Pedestrian`
3. `COCO PottedPlant`

\---

## 1\. Why does this repository use a mixed release model?

The three subsets have different provenance and redistribution conditions.

* `TrafficSigns` is directly released.
* `Cityscapes--Pedestrian` is released as a non-image reconstruction / metadata package.
* `COCO PottedPlant` is released as a metadata / reconstruction-first package.

This structure maximizes reproducibility while respecting upstream dataset terms.

\---

## 2\. Which subset includes actual image files?

`TrafficSigns` includes the actual released image files and YOLO labels.

They are stored under:

```text
traffic\\\_signs/Train\\\_Data/
```

The current structure is:

```text
traffic\\\_signs/Train\\\_Data/
    images/
        train/
        val/
    labels/
        train/
        val/
    test/
        images/
        labels/
```

\---

## 3\. Why are Cityscapes--Pedestrian images not included?

`Cityscapes--Pedestrian` is derived from Cityscapes.

This repository does **not** redistribute:

* original Cityscapes images
* derived cropped Cityscapes pedestrian images
* thumbnails or preview images derived from Cityscapes

Instead, it provides non-image public artifacts such as:

```text
cityscapes\\\_pedestrian/scripts/
cityscapes\\\_pedestrian/manifests/
cityscapes\\\_pedestrian/metadata/
cityscapes\\\_pedestrian/checksums/
cityscapes\\\_pedestrian/reconstruct\\\_cityscapes.py
```

Users must obtain Cityscapes separately and comply with the upstream Cityscapes terms.

\---

## 4\. Why are COCO PottedPlant images not included as a blanket release?

`COCO PottedPlant` is derived from MS-COCO images.

COCO images inherit upstream image rights, so this repository does not assume blanket permission to redistribute all derived cropped image files.

Instead, it provides reconstruction scripts, manifests, metadata, split documentation, checksums, and responsible-use notices.

Users must obtain COCO images and annotations separately and comply with the upstream terms that apply to those files.

\---

## 5\. How do I use TrafficSigns?

Use the released YOLO dataset structure:

```text
traffic\\\_signs/Train\\\_Data/
```

and the YOLO config:

```text
traffic\\\_signs/data.yaml
```

The current split counts are:

|Split|Count|
|-|-:|
|train|2256|
|val|451|
|test|302|
|total|3009|

The class mapping is:

```text
0 -> TrafficSigns
```

You can also test the loader and validation script:

```bash
python examples/load\\\_traffic\\\_signs.py
python examples/validate\\\_traffic\\\_signs.py
```

\---

## 6\. How do I reconstruct Cityscapes--Pedestrian?

Use the scripts in:

```text
cityscapes\\\_pedestrian/scripts/
```

The expected pipeline order is:

```text
01\\\_create\\\_crops\\\_from\\\_cityscapes\\\_with\\\_bb.py
02\\\_filter\\\_cropped\\\_images.py
03\\\_create\\\_yolo\\\_annotations\\\_from\\\_filtered.py
04\\\_draw\\\_yolo\\\_bb\\\_debug.py
05\\\_create\\\_yolo\\\_split\\\_structure.py
06\\\_build\\\_public\\\_manifest\\\_from\\\_local\\\_yolo.py
```

The pipeline requires upstream Cityscapes data obtained separately by the user.

The local reconstruction pipeline creates a local training-ready YOLO structure, but that local output is not redistributed by this repository.

The public manifest is:

```text
cityscapes\\\_pedestrian/manifests/cityscapes\\\_pedestrian\\\_manifest.csv
```

The current public manifest counts are:

|Split|Count|
|-|-:|
|train|1509|
|val|323|
|test|324|
|total|2156|

\---

## 7\. How do I reconstruct COCO PottedPlant?

Use the scripts in:

```text
coco\\\_pottedplant/scripts/
```

The expected pipeline order is:

```text
01\\\_extract\\\_pottedplant\\\_from\\\_coco\\\_to\\\_yolo.py
02\\\_create\\\_instance\\\_crops\\\_from\\\_yolo\\\_pottedplant.py
03\\\_draw\\\_cropped\\\_yolo\\\_bb\\\_debug.py
04\\\_build\\\_public\\\_manifest\\\_from\\\_local\\\_cropped\\\_yolo.py
```

The pipeline requires upstream COCO 2017 images and annotations obtained separately by the user.

The reconstruction pipeline:

1. extracts the `potted plant` category from COCO,
2. converts the subset to YOLO format,
3. creates `256x256` per-instance crops,
4. keeps intersecting potted-plant boxes in the cropped labels,
5. creates a public non-image manifest.

The public manifest is:

```text
coco\\\_pottedplant/manifests/coco\\\_pottedplant\\\_manifest.csv
```

The class mapping is:

```text
0 -> potted\\\_plant
```

\---

## 8\. What is a manifest?

A manifest is a machine-readable table that records information about released or reconstructed dataset records.

Manifest files may include:

* sample ID
* source image ID
* split membership
* class name
* number of boxes
* crop size
* source metadata
* notes about filtering or reconstruction

The main manifest files are:

```text
traffic\\\_signs/metadata/traffic\\\_signs\\\_manifest.csv
cityscapes\\\_pedestrian/manifests/cityscapes\\\_pedestrian\\\_manifest.csv
coco\\\_pottedplant/manifests/coco\\\_pottedplant\\\_manifest.csv
```

\---

## 9\. What is the difference between metadata and manifest files?

A **manifest** usually has one row per sample or released record.

A **metadata summary** describes the subset as a whole, including:

* release mode
* class map
* split counts
* source dataset
* pipeline settings
* notes

Examples:

```text
traffic\\\_signs/metadata/traffic\\\_signs\\\_summary.json
cityscapes\\\_pedestrian/metadata/cityscapes\\\_pedestrian\\\_summary.json
coco\\\_pottedplant/metadata/coco\\\_pottedplant\\\_summary.json
```

\---

## 10\. What are checksums for?

Checksums help verify file integrity.

For `TrafficSigns`, checksums cover directly released data files.

For `Cityscapes--Pedestrian` and `COCO PottedPlant`, checksums cover public non-image artifacts such as:

* scripts
* manifests
* metadata
* documentation
* reconstruction wrappers
* pipeline configuration files

Checksum files do not grant redistribution rights for upstream datasets.

\---

## 11\. Can I redistribute reconstructed Cityscapes or COCO crops?

Not automatically.

Cityscapes-derived and COCO-derived image crops inherit upstream restrictions.

Users must check and comply with upstream terms before redistributing any locally reconstructed image files.

This repository does not grant rights to upstream image data.

\---

## 12\. What should I read first?

Start with:

```text
README.md
```

Then read:

```text
docs/release\\\_matrix.md
docs/dataset\\\_card.md
docs/provenance.md
docs/ethics.md
```

For licensing notes, see:

```text
LICENSES/
```

\---

## 13\. What is the difference between public artifacts and local reconstruction outputs?

**Public artifacts** are files included in this repository or associated public release. These include:

* scripts
* metadata
* manifests
* checksums
* documentation
* reconstruction wrappers
* directly releasable TrafficSigns files

**Local reconstruction outputs** are files generated by users on their own machines after obtaining upstream datasets. These may include:

* Cityscapes-derived crops
* COCO-derived crops
* local YOLO training folders
* debug images with bounding boxes
* intermediate image folders

Local reconstruction outputs are not automatically redistributable.

\---

## 14\. Why does TrafficSigns have images but Cityscapes and COCO do not?

`TrafficSigns` is author-created and can be released directly.

`Cityscapes--Pedestrian` and `COCO PottedPlant` are derived from upstream datasets with their own redistribution constraints.

For those subsets, the repository releases reconstruction assets and metadata rather than redistributing image files directly.

\---

## 15\. Are the scripts meant to run on every machine?

The scripts are provided to document and reproduce the dataset preparation workflows.

Some scripts require local paths to upstream datasets. Users may need to edit path variables at the top of the scripts to match their own machines.

For example, reconstruction scripts may expect local folders such as:

```text
C:\\\\Users\\\\...\\\\Downloads\\\\Cityscapes\\\\
C:\\\\Users\\\\...\\\\Downloads\\\\COCO\\\_Dataset\\\\
```

The repository does not include those upstream datasets.

\---

## 16\. What should be updated if the dataset changes?

When a subset changes, update the relevant:

* manifest CSV
* summary JSON
* pipeline configuration JSON
* checksum file
* subset README
* `docs/dataset\\\_card.md`
* `docs/release\\\_matrix.md`
* `docs/provenance.md`
* `docs/ethics.md`

This keeps the repository internally consistent.

\---

## 17\. Where will citation information be stored?

Citation metadata will be stored in:

```text
CITATION.cff
```

A DOI-backed archival release should be created before or at submission time.



