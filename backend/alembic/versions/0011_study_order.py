"""Ordem editorial opcional, independente de domínio."""
from alembic import op
import sqlalchemy as sa

revision = '0011_study_order'
down_revision = '0010_study_practice'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('study_contents', sa.Column('study_order', sa.Integer(), nullable=True))
    op.create_check_constraint('ck_study_order', 'study_contents', 'study_order BETWEEN 1 AND 10000')


def downgrade() -> None:
    op.drop_constraint('ck_study_order', 'study_contents', type_='check')
    op.drop_column('study_contents', 'study_order')
