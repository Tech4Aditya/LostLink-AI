# LostLink Architecture

## Principles

1. Product services must not depend on a single ML model.
2. Reports are persisted before matching is attempted.
3. Matching failure never destroys a valid report.
4. AI produces candidate evidence, not ownership proof.
5. Private verification information is never public.
6. Model quality is measured on a held-out real dataset.
7. Every ML experiment must be reproducible.

## Runtime

```text
React/Vite
    |
FastAPI
    |
+---+--------------------+
|                        |
PostgreSQL + pgvector   Object storage
|
Matching service
|
SigLIP embeddings
|
candidate retrieval -> reranking -> verification
```

## Production evolution

- PostgreSQL/pgvector can remain the source of truth.
- Add Redis for background jobs when report volume requires it.
- Add a dedicated vector service only if PostgreSQL vector search becomes the bottleneck.
- Move images from local storage to private S3-compatible storage.
- Put API and worker containers behind a reverse proxy.
