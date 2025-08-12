from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID


class Principal(BaseModel):
    username: str
    role: str
    restaurant_id: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: str
    restaurant_id: Optional[str] = None
    restaurant_slug: Optional[str] = None
    exp: int


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str = Field(min_length=4)


class UserOut(UserBase):
    id: int
    created_at: datetime
class RestaurantBase(BaseModel):
    name: str
    username: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=4)
    is_active: bool = True


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantOut(BaseModel):
    id: UUID
    name: str
    slug: str
    logo_image: Optional[str] = None
    username: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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
    # Optional manager credential changes when saving settings
    manager_username: Optional[str] = None
    manager_password: Optional[str] = Field(default=None, min_length=4)


class SettingOut(SettingBase):
    id: int
    logo_path: Optional[str] = None
    barcode_image_path: Optional[str] = None
    updated_at: datetime
    manager_username: Optional[str] = None

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


