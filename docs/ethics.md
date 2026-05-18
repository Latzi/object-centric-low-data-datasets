\# Ethics and Responsible Use



This document describes ethics, responsible-use, privacy, and redistribution considerations for the \*\*Object-Centric Low-Data Datasets\*\* collection.



The collection contains three subsets:



1\. `TrafficSigns`

2\. `Cityscapes--Pedestrian`

3\. `COCO PottedPlant`



The repository uses a mixed release model because the subsets have different provenance, privacy, and redistribution conditions.



\---



\## 1. Intended use



This collection is intended for research on:



\- low-data object-centric image generation

\- few-shot generative modeling

\- synthetic data augmentation

\- object-centric representation learning

\- generative model evaluation

\- reconstruction-aware dataset release workflows

\- reproducible dataset curation pipelines



The resource is designed to support reproducible academic research under constrained-data conditions.



The intended use is research and benchmarking. Users should evaluate generated or augmented data carefully before using it in downstream systems.



\---



\## 2. Out-of-scope use



This collection is \*\*not\*\* intended for:



\- identity recognition

\- surveillance

\- tracking individuals

\- re-identification

\- inferring sensitive personal attributes

\- bypassing upstream dataset terms

\- redistributing upstream-restricted image data

\- replacing official upstream datasets

\- commercial use where upstream terms do not permit it

\- deployment in safety-critical systems without separate validation



Users are responsible for ensuring that their use of each subset complies with applicable institutional, legal, ethical, and upstream dataset requirements.



\---



\## 3. TrafficSigns



\### Release mode



`direct\_release`



\### What is released



`TrafficSigns` is the directly released subset in this collection.



The public package includes:



\- image files

\- YOLO label files

\- train / validation / test split structure

\- manifest CSV

\- summary metadata

\- checksum files

\- loader script

\- loading example

\- validation example



\### Responsible-use notes



This subset is intended for research on traffic-sign object-centric generation, augmentation, and evaluation.



Although this subset does not have the same upstream redistribution constraints as the Cityscapes- and COCO-derived subsets, users should still apply care when using it for downstream traffic or transport-related applications.



Users should not treat models trained or evaluated on this subset as ready for deployment in real traffic-control, autonomous-driving, or safety-critical systems without additional validation, testing, and domain-specific review.



\---



\## 4. Cityscapes--Pedestrian



\### Release mode



`abstract\_non\_image`



\### Source and privacy context



`Cityscapes--Pedestrian` is derived from upstream Cityscapes data and involves real-world urban scenes containing pedestrians.



The source imagery includes privacy protections such as face blurring. However, the subset should still be treated as sensitive because it is derived from real-world scenes involving people.



\### What is released



This repository provides public non-image artifacts such as:



\- reconstruction / preparation scripts

\- public manifest

\- summary metadata

\- pipeline configuration

\- split documentation

\- annotation documentation

\- checksum files

\- usage notes



\### What is not released



This repository does \*\*not\*\* redistribute:



\- original Cityscapes image files

\- derived cropped Cityscapes pedestrian images

\- thumbnails or preview images derived from Cityscapes

\- image exports that could act as substitutes for the Cityscapes-derived image subset



\### Responsible-use notes



Users must obtain Cityscapes separately and comply with the upstream Cityscapes terms.



This subset should not be used for:



\- identity recognition

\- surveillance

\- pedestrian tracking

\- re-identification

\- attempts to reverse or bypass privacy protections

\- human-subject analysis outside the scope of the upstream dataset terms



The reconstruction scripts are provided to support reproducibility for authorized users. They do not grant rights to the underlying Cityscapes images or to redistributed Cityscapes-derived crops.



See also:



\- `LICENSES/cityscapes\_notice.txt`

\- `docs/provenance.md`

\- `docs/release\_matrix.md`



\---



\## 5. COCO PottedPlant



\### Release mode



`metadata\_reconstruction\_first`



\### Source and rights context



`COCO PottedPlant` is derived from MS-COCO 2017 and uses images that originate from upstream sources. COCO annotations and image files do not necessarily share the same redistribution situation.



Because COCO images inherit upstream image rights, this repository does \*\*not\*\* assume blanket redistribution rights for all COCO-derived cropped image files.



\### What is released



This repository provides public reconstruction and metadata artifacts such as:



\- reconstruction / preparation scripts

\- public manifest

\- summary metadata

\- pipeline configuration

\- split documentation

\- annotation documentation

\- checksum files

\- usage notes



\### What is not released by default



This repository does \*\*not\*\* assume blanket public redistribution of:



\- original MS-COCO image files

\- all derived cropped COCO potted-plant images

\- thumbnails or previews derived from COCO images

\- image exports that would bypass upstream image rights



\### Responsible-use notes



Users must obtain COCO images and annotations separately and comply with the upstream terms that apply to those files.



The local reconstruction workflow generates object-centric potted-plant crops for research use. Users should not assume that the generated cropped images can be redistributed unless the relevant upstream image rights permit that redistribution.



The crop-generation pipeline keeps intersecting potted-plant boxes in cropped labels so that visible additional plants are not left unlabeled. Users should still verify labels before using reconstructed outputs in downstream experiments.



See also:



\- `LICENSES/coco\_notice.txt`

\- `docs/provenance.md`

\- `docs/release\_matrix.md`



\---



\## 6. Upstream dataset responsibilities



For subsets derived from upstream datasets, users are responsible for:



\- obtaining upstream data through official channels

\- complying with upstream licenses and terms

\- respecting redistribution constraints

\- citing upstream datasets where required

\- ensuring that local reconstructed outputs are used appropriately

\- confirming whether locally reconstructed crops may or may not be redistributed



This repository does not grant rights to any upstream image data.



The repository separates public metadata/reconstruction artifacts from locally reconstructed image outputs where upstream redistribution constraints require that distinction.



\---



\## 7. Synthetic data and generative modeling risks



Because this collection is intended for generative modeling and augmentation research, users should consider risks associated with synthetic data, including:



\- overfitting or memorization of small datasets

\- generation of misleading or unrealistic images

\- downstream model bias caused by synthetic augmentation

\- incorrect assumptions that synthetic data improves performance in all regimes

\- propagation of annotation errors into generated or augmented datasets

\- synthetic samples that appear plausible but degrade downstream performance

\- privacy concerns if models memorize or reproduce sensitive source data



Generated or augmented data should be evaluated carefully before use in downstream systems.



Researchers should report whether synthetic data improves, harms, or has no effect on downstream performance, rather than assuming that augmentation is always beneficial.



\---



\## 8. Documentation and transparency



Users should consult the following files before using or reconstructing the subsets:



\- `README.md`

\- `docs/dataset\_card.md`

\- `docs/release\_matrix.md`

\- `docs/provenance.md`

\- `docs/faq.md`

\- `LICENSES/traffic\_signs\_license.txt`

\- `LICENSES/cityscapes\_notice.txt`

\- `LICENSES/coco\_notice.txt`



These documents describe the release mode, provenance, intended use, and redistribution constraints for each subset.



Each subset also contains its own README files, metadata files, manifest files, and checksum files.



\---



\## 9. Maintenance



If the release mode, source data, preprocessing scripts, reconstruction workflow, manifests, or redistribution assumptions change, this ethics document should be updated together with:



\- `docs/dataset\_card.md`

\- `docs/release\_matrix.md`

\- `docs/provenance.md`

\- subset-level README files

\- subset-level metadata JSON files

\- subset-level pipeline configuration files

\- checksum files



If manifests are regenerated, corresponding checksum files should also be regenerated.



\---



\## 10. Reporting issues



Users who find problems with:



\- dataset documentation

\- manifests

\- scripts

\- labels

\- reconstruction instructions

\- licensing notices

\- responsible-use guidance



should report them through the repository issue tracker or contact the maintainers.



\---



\## 11. Disclaimer



This file is a responsible-use and ethics notice for the repository.



It is not a substitute for upstream license terms.



It does not constitute legal advice.



Users remain responsible for checking and complying with the terms that apply to any upstream datasets or locally reconstructed outputs they use.

