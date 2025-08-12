from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Table, Text, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..core.database import Base


# Association tables
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="RESTRICT"), primary_key=True),
    UniqueConstraint("product_id", "category_id", name="uq_product_category"),
)

product_ingredients = Table(
    "product_ingredients",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("ingredient_id", ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient"),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class Setting(Base, TimestampMixin):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(200), default="")
    logo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency_1: Mapped[str] = mapped_column(String(10), default="USD")
    currency_2: Mapped[str] = mapped_column(String(10), default="EUR")
    rate: Mapped[float] = mapped_column(Float, default=1.0)
    barcode_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    barcode_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    background_color: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=product_categories, back_populates="categories"
    )


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price_currency_1: Mapped[float] = mapped_column(Float, nullable=False)
    price_currency_2: Mapped[float] = mapped_column(Float, nullable=False)

    categories: Mapped[list[Category]] = relationship(
        secondary=product_categories, back_populates="products"
    )

    ingredients: Mapped[list["Ingredient"]] = relationship(
        secondary=product_ingredients, back_populates="products"
    )


class Ingredient(Base, TimestampMixin):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    products: Mapped[list[Product]] = relationship(
        secondary=product_ingredients, back_populates="ingredients"
    )


