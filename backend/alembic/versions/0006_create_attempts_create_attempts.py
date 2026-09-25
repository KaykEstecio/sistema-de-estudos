"""create_attempts

Revision ID: 0006_create_attempts
Revises: 0005_create_challenges
Create Date: 2026-09-24 19:45:33.391114
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0006_create_attempts'
down_revision: Union[str, Sequence[str], None] = '0005_create_challenges'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('challenge_attempts',
    sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('challenge_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), server_default='IN_PROGRESS', nullable=False),
    sa.Column('draft_answer', sa.String(length=20000), server_default='', nullable=False),
    sa.Column('attempt_number', sa.Integer(), nullable=False),
    sa.Column('challenge_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("(status = 'IN_PROGRESS' AND submitted_at IS NULL) OR (status = 'SUBMITTED' AND submitted_at IS NOT NULL)", name='ck_attempts_submission'),
    sa.CheckConstraint("jsonb_typeof(challenge_snapshot) = 'object'", name='ck_attempts_snapshot'),
    sa.CheckConstraint("status IN ('IN_PROGRESS','SUBMITTED')", name='ck_attempts_status'),
    sa.CheckConstraint('attempt_number > 0', name='ck_attempts_number'),
    sa.CheckConstraint('last_activity_at >= started_at AND (submitted_at IS NULL OR submitted_at >= started_at)', name='ck_attempts_dates'),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], name='fk_attempts_challenge', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_attempts_user', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'challenge_id', 'attempt_number', name='uq_attempts_number')
    )
    op.create_index('ix_attempts_challenge_id', 'challenge_attempts', ['challenge_id'], unique=False)
    op.create_index('uq_attempts_open', 'challenge_attempts', ['user_id', 'challenge_id'], unique=True, postgresql_where=sa.text("status = 'IN_PROGRESS'"))


def downgrade() -> None:
    op.drop_index('uq_attempts_open', table_name='challenge_attempts', postgresql_where=sa.text("status = 'IN_PROGRESS'"))
    op.drop_index('ix_attempts_challenge_id', table_name='challenge_attempts')
    op.drop_table('challenge_attempts')
