"""create_challenges

Revision ID: 0005_create_challenges
Revises: 0004_create_assessments
Create Date: 2026-09-24 14:46:57.806944
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0005_create_challenges'
down_revision: Union[str, Sequence[str], None] = '0004_create_assessments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('challenges',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.String(length=20000), nullable=False),
    sa.Column('challenge_type', sa.String(length=20), nullable=False),
    sa.Column('difficulty', sa.String(length=20), nullable=False),
    sa.Column('difficulty_score', sa.Integer(), nullable=False),
    sa.Column('estimated_minutes', sa.Integer(), nullable=False),
    sa.Column('starter_code', sa.String(length=20000), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("challenge_type IN ('QUIZ','CODE','BUG_FIX','CODE_READING','REFACTORING','SQL','API','ARCHITECTURE','PROJECT')", name='ck_challenges_type'),
    sa.CheckConstraint("difficulty IN ('VERY_EASY','EASY','MEDIUM','HARD','VERY_HARD')", name='ck_challenges_difficulty'),
    sa.CheckConstraint('char_length(btrim(description)) BETWEEN 1 AND 20000', name='ck_challenges_description'),
    sa.CheckConstraint('char_length(btrim(title)) BETWEEN 1 AND 200', name='ck_challenges_title'),
    sa.CheckConstraint('difficulty_score BETWEEN 0 AND 1000', name='ck_challenges_score'),
    sa.CheckConstraint('estimated_minutes BETWEEN 1 AND 1440', name='ck_challenges_minutes'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_challenges_active_id', 'challenges', ['is_active', 'id'], unique=False)
    op.create_table('challenge_skills',
    sa.Column('challenge_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('weight', sa.Integer(), nullable=False),
    sa.CheckConstraint('weight BETWEEN 1 AND 100', name='ck_challenge_skills_weight'),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], name='fk_challenge_skills_challenge', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], name='fk_challenge_skills_skill', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('challenge_id', 'skill_id')
    )
    op.create_index('ix_challenge_skills_skill_id', 'challenge_skills', ['skill_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_challenge_skills_skill_id', table_name='challenge_skills')
    op.drop_table('challenge_skills')
    op.drop_index('ix_challenges_active_id', table_name='challenges')
    op.drop_table('challenges')
