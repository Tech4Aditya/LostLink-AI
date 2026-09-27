# LostLink Dataset Specification

## Goal

Train/evaluate item-to-item retrieval, not generic object classification.

## Public data sources to investigate

1. COCO — broad object/category coverage.
2. Stanford Online Products — fine-grained product/image retrieval.
3. DeepFashion2 — fine-grained clothing, viewpoint and instance variation.

Always download datasets from their official/project pages and respect their licenses.

## Our proprietary dataset

The most valuable dataset will be confirmed LostLink cases:

```text
object_id
incident_id
lost/found
image(s)
description
category
color
brand if voluntarily provided
location
time
positive match group
verification outcome
```

## Positive pair

Two reports confirmed to concern the same physical object.

## Hard negative

Two reports that look deceptively similar but are known to be different objects.

Examples:
- two black backpacks
- two identical water bottles
- same phone model/color
- same clothing brand/model

## Split strategy

Split by physical object/incident, not by image.

Bad:

```text
photo_1 -> train
photo_2 -> test
```

Good:

```text
OBJ001 -> train
OBJ002 -> validation
OBJ003 -> test
```

## Augmentation

Useful:
- crop
- moderate blur
- brightness changes
- viewpoint changes
- background changes

Do not generate synthetic evidence and then report it as real-world accuracy.

## Metrics

Primary:
- Recall@1
- Recall@5
- Recall@10

Safety/product:
- false-match rate
- false-non-match rate
- calibration

## Fine-tuning plan

Stage 1:
pretrained SigLIP baseline.

Stage 2:
collect real confirmed pairs.

Stage 3:
contrastive/pairwise fine-tuning.

Stage 4:
hard-negative mining.

Stage 5:
re-evaluate on a locked test set.

Only promote a model if it beats the previous model on the locked test set.
