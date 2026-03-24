"""add notifications

Revision ID: 0002_add_notifications
Revises: 0001_initial_schema
Create Date: 2026-03-24 21:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_add_notifications"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("permit_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_permit_id"), "notifications", ["permit_id"], unique=False)
    op.create_index(op.f("ix_notifications_event_type"), "notifications", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_event_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_permit_id"), table_name="notifications")
    op.drop_table("notifications")
