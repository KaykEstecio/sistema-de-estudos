"""Cria categorias e competências preservando usuários."""

from alembic import op
import sqlalchemy as sa

revision = "0002_create_catalog"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_categories"),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
        sa.CheckConstraint("slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name="ck_categories_slug_format"),
    )
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_skills"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name="fk_skills_category_id", ondelete="RESTRICT"),
        sa.UniqueConstraint("slug", name="uq_skills_slug"),
        sa.CheckConstraint("slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name="ck_skills_slug_format"),
    )
    op.create_index("ix_skills_category_id", "skills", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_skills_category_id", table_name="skills")
    op.drop_table("skills")
    op.drop_table("categories")
