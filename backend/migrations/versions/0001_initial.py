from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(30), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("type", sa.String(10), nullable=False, index=True),
        sa.Column("category", sa.String(80), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("color", sa.String(60), nullable=True),
        sa.Column("location_name", sa.String(200), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="active", index=True),
        sa.Column("text_embedding", Vector(768), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "images",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("report_id", sa.UUID(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "matches",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("lost_report_id", sa.UUID(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("found_report_id", sa.UUID(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("visual_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("text_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("attribute_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("location_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("time_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("final_score", sa.Float(), nullable=False, server_default="0", index=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="candidate", index=True),
        sa.Column("explanation", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("lost_report_id", "found_report_id", name="uq_match_pair"),
    )
    op.create_table(
        "claims",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("match_id", sa.UUID(), sa.ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("claimant_user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("private_detail", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

def downgrade():
    op.drop_table("claims")
    op.drop_table("matches")
    op.drop_table("images")
    op.drop_table("reports")
    op.drop_table("users")
