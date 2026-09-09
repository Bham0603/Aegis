"""Add attack_runs table

Revision ID: ebdb65f49e1a
Revises: 33247aa65223
Create Date: 2026-09-09 00:42:07.016922

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ebdb65f49e1a"
down_revision: str | Sequence[str] | None = "33247aa65223"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "attack_runs",
        sa.Column("run_id", sa.String(), nullable=False),
        sa.Column("scenario_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("expected_result", sa.String(), nullable=False),
        sa.Column("actual_result", sa.String(), nullable=False),
        sa.Column("correlation_id", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_index(
        op.f("ix_attack_runs_correlation_id"),
        "attack_runs",
        ["correlation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attack_runs_scenario_id"), "attack_runs", ["scenario_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_attack_runs_scenario_id"), table_name="attack_runs")
    op.drop_index(op.f("ix_attack_runs_correlation_id"), table_name="attack_runs")
    op.drop_table("attack_runs")
