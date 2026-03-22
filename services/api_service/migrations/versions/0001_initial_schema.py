"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-03-22 22:40:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


permit_status = sa.Enum(
    "draft",
    "submitted",
    "under_review",
    "approved",
    "rejected",
    "in_progress",
    "completed",
    "cancelled",
    name="permitstatus",
)

approval_status = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="approvalstatus",
)


def upgrade() -> None:
    bind = op.get_bind()
    permit_status.create(bind, checkfirst=True)
    approval_status.create(bind, checkfirst=True)

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employees_full_name"), "employees", ["full_name"], unique=False)

    op.create_table(
        "facilities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("facility_type", sa.String(length=100), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_facilities_name"), "facilities", ["name"], unique=True)

    op.create_table(
        "work_types",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_work_types_name"), "work_types", ["name"], unique=True)

    op.create_table(
        "permits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", permit_status, nullable=False),
        sa.Column("safety_measures", sa.Text(), nullable=False),
        sa.Column("facility_id", sa.Integer(), nullable=False),
        sa.Column("work_type_id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.id"]),
        sa.ForeignKeyConstraint(["work_type_id"], ["work_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permits_title"), "permits", ["title"], unique=False)

    op.create_table(
        "permit_approvals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("permit_id", sa.Integer(), nullable=False),
        sa.Column("approver_employee_id", sa.Integer(), nullable=False),
        sa.Column("status", approval_status, nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(["approver_employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["permit_id"], ["permits.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "permit_status_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("permit_id", sa.Integer(), nullable=False),
        sa.Column("status", permit_status, nullable=False),
        sa.Column("note", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(["permit_id"], ["permits.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("permit_status_history")
    op.drop_table("permit_approvals")
    op.drop_index(op.f("ix_permits_title"), table_name="permits")
    op.drop_table("permits")
    op.drop_index(op.f("ix_work_types_name"), table_name="work_types")
    op.drop_table("work_types")
    op.drop_index(op.f("ix_facilities_name"), table_name="facilities")
    op.drop_table("facilities")
    op.drop_index(op.f("ix_employees_full_name"), table_name="employees")
    op.drop_table("employees")

    bind = op.get_bind()
    approval_status.drop(bind, checkfirst=True)
    permit_status.drop(bind, checkfirst=True)
