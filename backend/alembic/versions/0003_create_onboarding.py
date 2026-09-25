"""Persiste perfil declarado, interesses e objetivo principal."""

from alembic import op
import sqlalchemy as sa

revision = "0003_create_onboarding"
down_revision = "0002_create_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("declared_experience", sa.String(20), nullable=True))
    op.execute("UPDATE users SET onboarding_completed = false WHERE onboarding_completed = true")
    op.create_check_constraint("ck_users_declared_experience", "users",
        "declared_experience IN ('NEVER_PROGRAMMED','BEGINNER','BASIC','INTERMEDIATE','ADVANCED')")
    op.create_check_constraint("ck_users_onboarding_experience", "users",
        "NOT onboarding_completed OR declared_experience IS NOT NULL")
    op.create_table("user_interests",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_user_interests"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_interests_user", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name="fk_user_interests_category", ondelete="RESTRICT"),
        sa.UniqueConstraint("user_id", "category_id", name="uq_user_interests_user_category"),
        sa.CheckConstraint("priority >= 1", name="ck_user_interests_priority"))
    op.create_index("ix_user_interests_category_id", "user_interests", ["category_id"])
    op.create_table("user_goals",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_type", sa.String(120), nullable=False),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_user_goals"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_goals_user", ondelete="RESTRICT"))
    op.create_index("ix_user_goals_user_id", "user_goals", ["user_id"])
    op.create_index("uq_user_goals_primary", "user_goals", ["user_id"], unique=True, postgresql_where=sa.text("is_primary"))


def downgrade() -> None:
    op.drop_table("user_goals")
    op.drop_table("user_interests")
    op.execute("UPDATE users SET onboarding_completed = false WHERE onboarding_completed = true")
    op.drop_constraint("ck_users_onboarding_experience", "users", type_="check")
    op.drop_constraint("ck_users_declared_experience", "users", type_="check")
    op.drop_column("users", "declared_experience")
