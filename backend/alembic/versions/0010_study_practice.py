"""Prática editorial opcional por aula."""
from alembic import op
import sqlalchemy as sa

revision = '0010_study_practice'
down_revision = '0009_create_study'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('study_contents', sa.Column('challenge_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_study_practice', 'study_contents', 'challenges', ['challenge_id'], ['id'], ondelete='RESTRICT')


def downgrade() -> None:
    op.drop_constraint('fk_study_practice', 'study_contents', type_='foreignkey')
    op.drop_column('study_contents', 'challenge_id')
