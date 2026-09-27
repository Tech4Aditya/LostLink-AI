#!/bin/sh
set -eu

# 1) Wait for PostgreSQL and apply Alembic migrations.
i=0
until alembic upgrade head; do
  i=$((i + 1))
  if [ "$i" -ge 30 ]; then
    echo "Database migrations failed after 30 attempts."
    exit 1
  fi
  echo "Database not ready; retrying migrations in 2s ($i/30)..."
  sleep 2
done

# 2) Defensive local-schema bootstrap.
# Some older LostLink local volumes were stamped as migrated while the
# application tables were missing. create_all() is idempotent and only creates
# tables that are absent; it does not drop or overwrite existing data.
python - <<'PY'
from sqlalchemy import text
from app.db import engine, Base
from app import models  # noqa: F401

with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

Base.metadata.create_all(bind=engine, checkfirst=True)

with engine.connect() as conn:
    missing = conn.execute(text("""
        SELECT name
        FROM (VALUES ('users'), ('reports'), ('images'), ('matches'), ('claims')) AS expected(name)
        WHERE to_regclass('public.' || name) IS NULL
    """)).scalars().all()

if missing:
    raise RuntimeError(f"LostLink schema bootstrap failed; missing tables: {missing}")

print("LostLink database schema verified: users, reports, images, matches, claims")
PY

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
