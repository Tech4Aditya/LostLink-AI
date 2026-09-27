# LostLink AI


https://github.com/user-attachments/assets/d17d2eea-3dc4-44ae-90f8-2baebb5c27cf

<img width="1350" height="734" alt="image" src="https://github.com/user-attachments/assets/624af832-cc50-4dac-820f-ab5ca96bf6f0" />

<img width="943" height="469" alt="Screenshot 2026-09-27 140123" src="https://github.com/user-attachments/assets/8ec30ee4-8ad8-4812-8135-082dd9e0e76b" />


A production-minded Lost & Found matching platform built around multimodal retrieval, metadata ranking, privacy-first ownership verification, and a real evaluation pipeline.

## What this repository contains

- `backend/` — FastAPI API, PostgreSQL/pgvector models, auth, reports, matching, verification
- `frontend/` — React + Vite dashboard and reporting UI
- `ai/` — model/evaluation/training utilities
- `infra/` — Docker Compose for PostgreSQL + pgvector and the application services
- `docs/` — architecture and ML/data specification
- `data/` — dataset manifest/templates
- `scripts/` — Windows/Linux helper scripts

The architecture deliberately separates the product from the ML system. If the model is unavailable, reporting and browsing still work and the backend falls back to deterministic text/metadata matching instead of crashing.

## Recommended development environment

- Docker Desktop
- Python 3.11+
- Node.js 20+
- Git

For local AI inference, expect the first SigLIP model download to be large. The model is loaded lazily, so the API can start before the model is downloaded.

## Quick start with Docker

1. Copy `.env.example` to `.env`.
2. Start services:

```bash
docker compose -f infra/docker-compose.yml up --build
```

3. Open:
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - Swagger: http://localhost:8000/docs

The first AI inference downloads the configured Hugging Face model.

## Local development without Docker

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL="postgresql+psycopg://lostlink:lostlink@localhost:5432/lostlink"
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## AI modes

`.env`:

```env
AI_ENABLED=true
AI_MODEL_ID=google/siglip-base-patch16-224
```

For a fast smoke test without downloading a model:

```env
AI_ENABLED=false
```

The application still creates reports and computes deterministic candidate scores from text + category + color + location + time.

## Important product rule

AI results are **candidate matches**, not proof of ownership.

The flow is:

```text
Lost/Found report
       ↓
Multimodal candidate retrieval
       ↓
Metadata + semantic reranking
       ↓
Potential match
       ↓
Private ownership challenge
       ↓
Human/admin review when required
       ↓
Reunification
```

Never expose private verification answers in a public listing.

## ML workflow

Do not fine-tune the model on day one.

1. Launch the retrieval baseline.
2. Collect real lost/found reports.
3. Record confirmed matches and rejected candidates.
4. Build positive pairs and hard negatives.
5. Split by object/event identity to prevent leakage.
6. Evaluate Recall@1/5/10, precision, false-match rate and false-non-match rate.
7. Fine-tune only after the baseline and dataset are stable.

See `docs/ML_DATASET.md`.

## Security before public deployment

This repo is an engineering foundation, not a claim that a campus deployment is automatically secure.

Before production:
- move uploads to private object storage
- use signed URLs
- enable HTTPS
- rotate JWT secret
- add rate limiting
- add virus/content scanning for uploads
- add audit logging
- add database backups
- add admin role enforcement
- encrypt sensitive verification data
- add abuse reporting and retention policies

## Local startup

1. Make sure Docker Desktop is running.
2. From the project root: `docker compose -f infra/docker-compose.yml up --build`
3. Open `http://localhost:5173`.

The frontend uses a Vite proxy for `/api` and `/uploads`, so local browser requests stay same-origin and do not depend on browser CORS configuration. The backend still has explicit CORS support for direct API access.

If you previously ran an older LostLink build, rebuild the backend and frontend so stale Docker layers cannot be reused:

```powershell
docker compose -f infra/docker-compose.yml down
docker compose -f infra/docker-compose.yml build --no-cache backend frontend
docker compose -f infra/docker-compose.yml up
```

This does **not** delete the PostgreSQL volume. Do not use `down -v` unless you intentionally want to erase the local database.

### Optional demo account

```powershell
docker compose -f infra/docker-compose.yml exec backend python -m app.seed
```

Demo credentials: `demo@lostlink.ai` / `DemoPass123!`

## Database migration recovery

The backend includes an idempotent `0002_repair_schema` migration. It repairs a local
PostgreSQL volume that was previously marked at migration `0001_initial` even though
the application tables were not created. This avoids requiring `docker compose down -v`
and preserves existing PostgreSQL data.

## Local database repair

The backend startup is defensive for local development. After Alembic migrations it runs an idempotent SQLAlchemy `create_all(checkfirst=True)` and verifies that `users`, `reports`, `images`, `matches`, and `claims` exist. This repairs older local volumes that were incorrectly stamped as migrated.

If the stack is already running, use:

```powershell
.\scripts\repair-db.ps1
```
