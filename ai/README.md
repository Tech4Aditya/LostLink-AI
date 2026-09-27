# LostLink ML

This directory is deliberately separated from the backend.

## Baseline

The API uses a lazy pretrained SigLIP encoder for:
- image embeddings
- text embeddings

The current model is configured through `AI_MODEL_ID`.

## Training data

Do not mix train and test examples from the same physical object.

Recommended split key:

```text
object_id / incident_id
```

not image filename.

## Target metrics

- Recall@1
- Recall@5
- Recall@10
- Precision
- false-match rate
- false-non-match rate
- calibration of candidate score

See `docs/ML_DATASET.md`.
