"""create_assessments

Revision ID: 0004_create_assessments
Revises: 0003_create_onboarding
Create Date: 2026-09-24 14:08:07.312101
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0004_create_assessments'
down_revision: Union[str, Sequence[str], None] = '0003_create_onboarding'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('assessments',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('assessment_type', sa.String(length=20), server_default='INITIAL', nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("assessment_type = 'INITIAL'", name='ck_assessments_type'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_assessments_user', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'], unique=False)
    op.create_index('uq_assessments_open_user', 'assessments', ['user_id'], unique=True, postgresql_where=sa.text('completed_at IS NULL'))
    op.create_table('assessment_items',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('prompt', sa.String(length=4000), nullable=False),
    sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('correct_option', sa.String(length=1), nullable=False),
    sa.Column('selected_option', sa.String(length=1), nullable=True),
    sa.CheckConstraint("correct_option IN ('A','B','C','D')", name='ck_assessment_items_correct'),
    sa.CheckConstraint("selected_option IN ('A','B','C','D')", name='ck_assessment_items_selected'),
    sa.CheckConstraint('position > 0', name='ck_assessment_items_position'),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], name='fk_assessment_items_assessment', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], name='fk_assessment_items_skill', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('assessment_id', 'position', name='uq_assessment_items_position')
    )
    op.create_index('ix_assessment_items_skill_id', 'assessment_items', ['skill_id'], unique=False)
    op.create_table('assessment_questions',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('code', sa.String(length=120), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('prompt', sa.String(length=4000), nullable=False),
    sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('correct_option', sa.String(length=1), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.CheckConstraint("code ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name='ck_assessment_questions_code'),
    sa.CheckConstraint("correct_option IN ('A','B','C','D')", name='ck_assessment_questions_correct'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], name='fk_assessment_questions_skill', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code', name='uq_assessment_questions_code')
    )
    op.create_index('ix_assessment_questions_skill_id', 'assessment_questions', ['skill_id'], unique=False)
    op.create_table('assessment_results',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
    sa.Column('correct_count', sa.Integer(), nullable=False),
    sa.Column('question_count', sa.Integer(), nullable=False),
    sa.CheckConstraint('confidence BETWEEN 0 AND 1', name='ck_assessment_results_confidence'),
    sa.CheckConstraint('question_count > 0 AND correct_count >= 0 AND correct_count <= question_count', name='ck_assessment_results_counts'),
    sa.CheckConstraint('score BETWEEN 0 AND 1000', name='ck_assessment_results_score'),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], name='fk_assessment_results_assessment', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], name='fk_assessment_results_skill', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('assessment_id', 'skill_id', name='uq_assessment_results_skill')
    )
    op.create_index('ix_assessment_results_skill_id', 'assessment_results', ['skill_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_assessment_results_skill_id', table_name='assessment_results')
    op.drop_table('assessment_results')
    op.drop_index('ix_assessment_questions_skill_id', table_name='assessment_questions')
    op.drop_table('assessment_questions')
    op.drop_index('ix_assessment_items_skill_id', table_name='assessment_items')
    op.drop_table('assessment_items')
    op.drop_index('uq_assessments_open_user', table_name='assessments', postgresql_where=sa.text('completed_at IS NULL'))
    op.drop_index('ix_assessments_user_id', table_name='assessments')
    op.drop_table('assessments')
