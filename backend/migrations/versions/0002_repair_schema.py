"""Repair databases that were stamped with 0001 before the full schema existed.

This migration is intentionally idempotent. It is safe on both a fresh database
and an existing local database whose alembic_version already says 0001 but whose
application tables are missing.
"""

from alembic import op

revision = "0002_repair_schema"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    # The old local build could have advanced alembic_version to 0001 without
    # actually having the application tables. Recreate the expected schema
    # defensively instead of asking the user to delete their database volume.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            email VARCHAR(320) NOT NULL UNIQUE,
            name VARCHAR(120) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(30) NOT NULL DEFAULT 'user',
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id UUID PRIMARY KEY,
            user_id UUID REFERENCES users(id),
            type VARCHAR(10) NOT NULL,
            category VARCHAR(80) NOT NULL,
            description TEXT NOT NULL,
            color VARCHAR(60),
            location_name VARCHAR(200) NOT NULL,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            event_time TIMESTAMPTZ,
            status VARCHAR(30) NOT NULL DEFAULT 'active',
            text_embedding vector(768),
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_reports_user_id ON reports (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reports_type ON reports (type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reports_category ON reports (category)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reports_status ON reports (status)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id UUID PRIMARY KEY,
            report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
            storage_path VARCHAR(500) NOT NULL,
            mime_type VARCHAR(100) NOT NULL,
            embedding vector(768),
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_images_report_id ON images (report_id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id UUID PRIMARY KEY,
            lost_report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
            found_report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
            visual_score DOUBLE PRECISION NOT NULL DEFAULT 0,
            text_score DOUBLE PRECISION NOT NULL DEFAULT 0,
            attribute_score DOUBLE PRECISION NOT NULL DEFAULT 0,
            location_score DOUBLE PRECISION NOT NULL DEFAULT 0,
            time_score DOUBLE PRECISION NOT NULL DEFAULT 0,
            final_score DOUBLE PRECISION NOT NULL DEFAULT 0,
            status VARCHAR(30) NOT NULL DEFAULT 'candidate',
            explanation JSON NOT NULL DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL,
            CONSTRAINT uq_match_pair UNIQUE (lost_report_id, found_report_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_matches_lost_report_id ON matches (lost_report_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_matches_found_report_id ON matches (found_report_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_matches_final_score ON matches (final_score)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_matches_status ON matches (status)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id UUID PRIMARY KEY,
            match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            claimant_user_id UUID REFERENCES users(id),
            private_detail TEXT,
            status VARCHAR(30) NOT NULL DEFAULT 'pending',
            review_notes TEXT,
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_claims_match_id ON claims (match_id)")


def downgrade():
    # Do not destroy user data during a repair downgrade.
    pass
