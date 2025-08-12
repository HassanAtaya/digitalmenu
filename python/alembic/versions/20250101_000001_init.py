"""init

Revision ID: 20250101_000001
Revises: 
Create Date: 2025-01-01 00:00:01.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250101_000001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('company_name', sa.String(length=200), nullable=True),
        sa.Column('logo_path', sa.String(length=255), nullable=True),
        sa.Column('currency_1', sa.String(length=10), nullable=True),
        sa.Column('currency_2', sa.String(length=10), nullable=True),
        sa.Column('rate', sa.Float(), nullable=True),
        sa.Column('barcode_url', sa.Text(), nullable=True),
        sa.Column('barcode_image_path', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('image_path', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_unique_constraint('uq_category_name', 'categories', ['name'])

    op.create_table(
        'ingredients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_unique_constraint('uq_ingredient_name', 'ingredients', ['name'])

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('image_path', sa.String(length=255), nullable=True),
        sa.Column('price_currency_1', sa.Float(), nullable=False),
        sa.Column('price_currency_2', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'product_categories',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('product_id', 'category_id'),
    )
    op.create_unique_constraint('uq_product_category', 'product_categories', ['product_id', 'category_id'])

    op.create_table(
        'product_ingredients',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('product_id', 'ingredient_id'),
    )
    op.create_unique_constraint('uq_product_ingredient', 'product_ingredients', ['product_id', 'ingredient_id'])


def downgrade() -> None:
    op.drop_constraint('uq_product_ingredient', 'product_ingredients', type_='unique')
    op.drop_table('product_ingredients')
    op.drop_constraint('uq_product_category', 'product_categories', type_='unique')
    op.drop_table('product_categories')
    op.drop_table('products')
    op.drop_constraint('uq_ingredient_name', 'ingredients', type_='unique')
    op.drop_table('ingredients')
    op.drop_constraint('uq_category_name', 'categories', type_='unique')
    op.drop_table('categories')
    op.drop_table('settings')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')


