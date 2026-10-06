"""Conteúdos de estudo e conclusão de leitura sem evidências de desempenho."""
from alembic import op
import sqlalchemy as sa

revision = '0009_create_study'
down_revision = '0008_create_user_skills'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('study_contents',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('skill_id', sa.Integer(), sa.ForeignKey('skills.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('explanation', sa.String(12000), nullable=False),
        sa.Column('code_example', sa.String(12000), nullable=False),
        sa.Column('common_mistakes', sa.String(6000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('char_length(btrim(title)) BETWEEN 1 AND 200', name='ck_study_title'),
        sa.CheckConstraint('char_length(btrim(explanation)) BETWEEN 1 AND 12000', name='ck_study_explanation'),
        sa.CheckConstraint('char_length(btrim(code_example)) BETWEEN 1 AND 12000', name='ck_study_example'),
        sa.CheckConstraint('char_length(btrim(common_mistakes)) BETWEEN 1 AND 6000', name='ck_study_mistakes'))
    op.create_index('ix_study_contents_skill_id', 'study_contents', ['skill_id'])
    op.create_table('study_completions',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='RESTRICT'), primary_key=True),
        sa.Column('content_id', sa.Integer(), sa.ForeignKey('study_contents.id', ondelete='RESTRICT'), primary_key=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    op.drop_table('study_completions')
    op.drop_index('ix_study_contents_skill_id', table_name='study_contents')
    op.drop_table('study_contents')
