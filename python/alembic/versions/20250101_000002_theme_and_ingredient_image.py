"""theme and ingredient image

Revision ID: 20250101_000002
Revises: 20250101_000001
Create Date: 2025-01-01 00:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '20250101_000002'
down_revision: Union[str, None] = '20250101_000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ingredients', sa.Column('image_path', sa.String(length=255), nullable=True))
    op.add_column('settings', sa.Column('primary_color', sa.String(length=20), nullable=True))
    op.add_column('settings', sa.Column('background_color', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('settings', 'background_color')
    op.drop_column('settings', 'primary_color')
    op.drop_column('ingredients', 'image_path')


