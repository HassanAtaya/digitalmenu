"""multi-restaurant scope

Revision ID: 20250101_000003
Revises: 20250101_000002
Create Date: 2025-01-01 00:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '20250101_000003'
down_revision: Union[str, None] = '20250101_000002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create restaurants
    op.create_table(
        'restaurants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('logo_image', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.UniqueConstraint('name', name='uq_restaurant_name'),
        sa.UniqueConstraint('slug', name='uq_restaurant_slug'),
        sa.UniqueConstraint('username', name='uq_restaurant_username'),
    )
    op.create_index('ix_restaurants_slug', 'restaurants', ['slug'], unique=False)

    # Scope settings
    op.add_column('settings', sa.Column('restaurant_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_settings_restaurant_id', 'settings', ['restaurant_id'])
    op.create_foreign_key('fk_settings_restaurant', 'settings', 'restaurants', ['restaurant_id'], ['id'], ondelete='CASCADE')

    # Scope categories
    # Remove global unique on name if exists
    try:
        op.drop_constraint('uq_category_name', 'categories', type_='unique')
    except Exception:
        pass
    op.add_column('categories', sa.Column('restaurant_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_categories_restaurant_id', 'categories', ['restaurant_id'])
    op.create_foreign_key('fk_categories_restaurant', 'categories', 'restaurants', ['restaurant_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('uq_category_restaurant_name', 'categories', ['restaurant_id', 'name'])

    # Scope products
    op.add_column('products', sa.Column('restaurant_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_products_restaurant_id', 'products', ['restaurant_id'])
    op.create_foreign_key('fk_products_restaurant', 'products', 'restaurants', ['restaurant_id'], ['id'], ondelete='CASCADE')
    # Drop price_currency_2 as we compute on view
    with op.batch_alter_table('products') as b:
        try:
            b.drop_column('price_currency_2')
        except Exception:
            pass

    # Scope ingredients
    try:
        op.drop_constraint('uq_ingredient_name', 'ingredients', type_='unique')
    except Exception:
        pass
    op.add_column('ingredients', sa.Column('restaurant_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_ingredients_restaurant_id', 'ingredients', ['restaurant_id'])
    op.create_foreign_key('fk_ingredients_restaurant', 'ingredients', 'restaurants', ['restaurant_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('uq_ingredient_restaurant_name', 'ingredients', ['restaurant_id', 'name'])

    # No change to association tables; integrity is enforced by fk cascades


def downgrade() -> None:
    # Ingredients
    try:
        op.drop_constraint('uq_ingredient_restaurant_name', 'ingredients', type_='unique')
    except Exception:
        pass
    try:
        op.drop_constraint('fk_ingredients_restaurant', 'ingredients', type_='foreignkey')
    except Exception:
        pass
    op.drop_index('ix_ingredients_restaurant_id', table_name='ingredients')
    with op.batch_alter_table('ingredients') as b:
        try:
            b.drop_column('restaurant_id')
        except Exception:
            pass
    # Categories
    try:
        op.drop_constraint('uq_category_restaurant_name', 'categories', type_='unique')
    except Exception:
        pass
    try:
        op.drop_constraint('fk_categories_restaurant', 'categories', type_='foreignkey')
    except Exception:
        pass
    op.drop_index('ix_categories_restaurant_id', table_name='categories')
    with op.batch_alter_table('categories') as b:
        try:
            b.drop_column('restaurant_id')
        except Exception:
            pass
    # Products
    try:
        op.drop_constraint('fk_products_restaurant', 'products', type_='foreignkey')
    except Exception:
        pass
    op.drop_index('ix_products_restaurant_id', table_name='products')
    with op.batch_alter_table('products') as b:
        try:
            b.add_column(sa.Column('price_currency_2', sa.Float(), nullable=True))
            b.drop_column('restaurant_id')
        except Exception:
            pass
    # Settings
    try:
        op.drop_constraint('fk_settings_restaurant', 'settings', type_='foreignkey')
    except Exception:
        pass
    op.drop_index('ix_settings_restaurant_id', table_name='settings')
    with op.batch_alter_table('settings') as b:
        try:
            b.drop_column('restaurant_id')
        except Exception:
            pass
    # Restaurants
    op.drop_index('ix_restaurants_slug', table_name='restaurants')
    op.drop_table('restaurants')


