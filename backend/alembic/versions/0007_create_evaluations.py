"""Persiste avaliações manuais e evidências qualitativas por skill."""

from alembic import op
import sqlalchemy as sa

revision = "0007_create_evaluations"
down_revision = "0006_create_attempts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attempt_evaluations",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("rubric_version", sa.String(30), server_default="manual-v1", nullable=False),
        sa.Column("feedback", sa.String(4000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["attempt_id"], ["challenge_attempts.id"], name="fk_evaluations_attempt", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], name="fk_evaluations_reviewer", ondelete="RESTRICT"),
        sa.UniqueConstraint("attempt_id", name="uq_evaluations_attempt"),
        sa.CheckConstraint("rubric_version = 'manual-v1'", name="ck_evaluations_rubric"),
        sa.CheckConstraint("feedback ~ '[^[:space:]]'", name="ck_evaluations_feedback"),
    )
    op.create_index("ix_evaluations_reviewer", "attempt_evaluations", ["reviewer_id"])
    op.create_table(
        "attempt_evaluation_skills",
        sa.Column("evaluation_id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("classification", sa.String(30), nullable=False),
        sa.Column("justification", sa.String(2000), nullable=False),
        sa.ForeignKeyConstraint(["evaluation_id"], ["attempt_evaluations.id"], name="fk_evaluation_skills_evaluation", ondelete="RESTRICT"),
        sa.CheckConstraint("skill_id > 0", name="ck_evaluation_skills_id"),
        sa.CheckConstraint("classification IN ('NOT_MET','PARTIALLY_MET','MET','INSUFFICIENT_EVIDENCE')", name="ck_evaluation_skills_classification"),
        sa.CheckConstraint("justification ~ '[^[:space:]]'", name="ck_evaluation_skills_justification"),
    )


def downgrade() -> None:
    op.drop_table("attempt_evaluation_skills")
    op.drop_index("ix_evaluations_reviewer", table_name="attempt_evaluations")
    op.drop_table("attempt_evaluations")
