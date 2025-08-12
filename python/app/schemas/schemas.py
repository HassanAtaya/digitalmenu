from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str = Field(min_length=4)


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SettingBase(BaseModel):
    company_name: str
    currency_1: str
    currency_2: str
    rate: float
    barcode_url: Optional[str] = None
    primary_color: Optional[str] = "#C9A24B"
    background_color: Optional[str] = "#0F0F0F"


class SettingCreate(SettingBase):
    pass


class SettingOut(SettingBase):
    id: int
    logo_path: Optional[str] = None
    barcode_image_path: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    image_path: Optional[str] = None

    class Config:
        from_attributes = True


class IngredientBase(BaseModel):
    name: str


class IngredientCreate(IngredientBase):
    pass


class IngredientOut(IngredientBase):
    id: int
    image_path: Optional[str] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    price_currency_1: float
    category_ids: List[int] = []
    ingredient_ids: List[int] = []


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    image_path: Optional[str] = None
    price_currency_2: float

    class Config:
        from_attributes = True


