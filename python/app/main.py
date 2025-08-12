from pathlib import Path
from typing import List, Optional
import uuid
from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .core.config import settings
from .core.database import Base, engine, get_db
from .core.security import create_access_token, verify_password, get_password_hash
from .dependencies import get_current_user, get_current_principal
from .models.models import (
    User,
    Setting,
    Category,
    Product,
    Ingredient,
    Restaurant,
    product_categories,
    product_ingredients,
)
from .schemas.schemas import (
    Token,
    UserOut,
    SettingOut,
    SettingCreate,
    RestaurantCreate,
    RestaurantOut,
    CategoryOut,
    CategoryCreate,
    IngredientOut,
    IngredientCreate,
    ProductOut,
    ProductCreate,
)


app = FastAPI(title=settings.app_name)

# CORS setup - adjust in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


media_path = Path(settings.media_dir)
media_path.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_path)), name="media")


@app.on_event("startup")
def on_startup():
    # Create tables if not exists (alembic handles migrations; this is for safety in dev)
    Base.metadata.create_all(bind=engine)
    # Seed default admin
    with Session(bind=engine) as db:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(username="admin", password_hash=get_password_hash("evolusys"))
            db.add(admin)
            db.commit()
        # seed demo restaurant if none exists
        if db.query(Restaurant).count() == 0:
            demo = Restaurant(name="La Famiglia", slug="la-famiglia", username="lafamiglia", password_hash=get_password_hash("secret"), is_active=True)
            db.add(demo)
            db.flush()
            setting = Setting(restaurant_id=demo.id, company_name="La Famiglia", currency_1="USD", currency_2="EUR", rate=1.0)
            db.add(setting)
            db.commit()


api = FastAPI()


@api.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Admin login
    user = db.query(User).filter(User.username == form_data.username).first()
    if user and verify_password(form_data.password, user.password_hash):
        token = create_access_token(subject=user.username, role="admin")
        return {"access_token": token, "token_type": "bearer"}

    # Restaurant manager login
    restaurant = db.query(Restaurant).filter(Restaurant.username == form_data.username).first()
    if restaurant and restaurant.password_hash and verify_password(form_data.password, restaurant.password_hash):
        token = create_access_token(
            subject=restaurant.username or restaurant.slug,
            role="manager",
            restaurant_id=str(restaurant.id),
            restaurant_slug=restaurant.slug,
        )
        return {"access_token": token, "token_type": "bearer"}
def _ensure_admin(principal: dict):
    if not principal or principal.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")


def _ensure_admin_or_restaurant(principal: dict, restaurant_slug: str, db: Session):
    if principal.get("role") == "admin":
        return
    if principal.get("role") == "manager":
        rid = principal.get("restaurant_id")
        rslug = principal.get("restaurant_slug")
        if not rid:
            raise HTTPException(status_code=403, detail="Forbidden")
        r = _get_restaurant_by_slug(db, restaurant_slug)
        if str(r.id) != rid:
            raise HTTPException(status_code=403, detail="Forbidden")
        return
    raise HTTPException(status_code=403, detail="Forbidden")


    raise HTTPException(status_code=400, detail="Incorrect username or password")


def _get_restaurant_by_slug(db: Session, slug: str) -> Restaurant:
    r = db.query(Restaurant).filter(Restaurant.slug == slug).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return r


def _get_restaurant_by_id_or_slug(db: Session, id_or_slug: str) -> Restaurant:
    # Try UUID
    try:
        rid = uuid.UUID(id_or_slug)
        r = db.query(Restaurant).filter(Restaurant.id == rid).first()
        if r:
            return r
    except Exception:
        pass
    # Fallback by slug
    return _get_restaurant_by_slug(db, id_or_slug)


# Admin: restaurants
@api.get("/admin/restaurants", response_model=List[RestaurantOut])
def list_restaurants(db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin(principal)
    # current implementation assumes any authenticated user in users table is admin
    items = db.query(Restaurant).order_by(Restaurant.created_at.desc()).all()
    return items


def _slugify(name: str) -> str:
    import re

    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", name).strip().lower()
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug


@api.post("/admin/restaurants", response_model=RestaurantOut)
def create_restaurant(payload: RestaurantCreate, request: Request, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin(principal)
    base = str(request.base_url).rstrip('/')
    base_slug = _slugify(payload.name)
    slug = base_slug
    i = 1
    while db.query(Restaurant).filter(Restaurant.slug == slug).first() is not None:
        i += 1
        slug = f"{base_slug}-{i}"
    rest = Restaurant(name=payload.name, slug=slug, is_active=payload.is_active)
    if payload.username:
        rest.username = payload.username
    if payload.password:
        rest.password_hash = get_password_hash(payload.password)
    db.add(rest)
    db.flush()
    # default settings per restaurant
    setting = Setting(
        restaurant_id=rest.id,
        company_name=payload.name,
        currency_1="USD",
        currency_2="EUR",
        rate=1.0,
        primary_color="#C9A24B",
        background_color="#0F0F0F",
    )
    db.add(setting)
    db.commit()
    db.refresh(rest)
    return rest


@api.get("/admin/restaurants/{id_or_slug}", response_model=RestaurantOut)
def get_restaurant(id_or_slug: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin(principal)
    return _get_restaurant_by_id_or_slug(db, id_or_slug)


@api.put("/admin/restaurants/{id_or_slug}", response_model=RestaurantOut)
def update_restaurant(id_or_slug: str, payload: RestaurantCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin(principal)
    rest = _get_restaurant_by_id_or_slug(db, id_or_slug)
    rest.name = payload.name
    rest.is_active = payload.is_active
    if payload.username is not None:
        rest.username = payload.username
    if payload.password:
        rest.password_hash = get_password_hash(payload.password)
    db.commit()
    db.refresh(rest)
    return rest


@api.delete("/admin/restaurants/{id_or_slug}")
def delete_restaurant(id_or_slug: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin(principal)
    rest = _get_restaurant_by_id_or_slug(db, id_or_slug)
    # Block deletion if any child data exists
    has_children = (
        db.query(Category).filter(Category.restaurant_id == rest.id).first() is not None or
        db.query(Product).filter(Product.restaurant_id == rest.id).first() is not None or
        db.query(Ingredient).filter(Ingredient.restaurant_id == rest.id).first() is not None
    )
    if has_children:
        raise HTTPException(status_code=400, detail="Cannot delete restaurant with existing data")
    db.delete(rest)
    db.commit()
    return {"status": "ok"}


@api.post("/admin/restaurants/{id_or_slug}/toggle-active")
def toggle_restaurant_active(id_or_slug: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin(principal)
    rest = _get_restaurant_by_id_or_slug(db, id_or_slug)
    rest.is_active = not rest.is_active
    db.commit()
    return {"is_active": rest.is_active}


# Scoped settings per restaurant
@api.get("/restaurants/{slug}/settings", response_model=SettingOut)
def get_settings(slug: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    setting = db.query(Setting).filter(Setting.restaurant_id == rest.id).first()
    if not setting:
        setting = Setting(restaurant_id=rest.id, company_name=rest.name, currency_1="USD", currency_2="EUR", rate=1.0)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    # attach manager_username to response for UI convenience
    result = {
        **{k: getattr(setting, k) for k in setting.__dict__ if not k.startswith("_")},
        "manager_username": rest.username,
    }
    return result


@api.post("/restaurants/{slug}/settings", response_model=SettingOut)
def save_settings(slug: str, payload: SettingCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    setting = db.query(Setting).filter(Setting.restaurant_id == rest.id).first()
    if not setting:
        setting = Setting(restaurant_id=rest.id, **payload.model_dump())
        db.add(setting)
    else:
        data = payload.model_dump()
        for k, v in data.items():
            if k in ("manager_username", "manager_password"):
                continue
            setattr(setting, k, v)
    # Update manager credentials if provided
    if payload.manager_username is not None:
        rest.username = payload.manager_username or None
    if payload.manager_password:
        rest.password_hash = get_password_hash(payload.manager_password)
    db.commit()
    db.refresh(setting)
    result = {
        **{k: getattr(setting, k) for k in setting.__dict__ if not k.startswith("_")},
        "manager_username": rest.username,
    }
    return result


@api.post("/restaurants/{slug}/settings/logo", response_model=SettingOut)
async def upload_logo(slug: str, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    setting = db.query(Setting).filter(Setting.restaurant_id == rest.id).first()
    if not setting:
        setting = Setting(restaurant_id=rest.id, company_name=rest.name, currency_1="USD", currency_2="EUR", rate=1.0)
        db.add(setting)
        db.commit()
        db.refresh(setting)

    file_ext = Path(file.filename).suffix
    dest = media_path / f"{rest.slug}_logo{file_ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    setting.logo_path = f"{base}/media/{dest.name}"
    # also reflect on restaurant logo_image for quick public usage
    rest.logo_image = setting.logo_path
    db.commit()
    db.refresh(setting)
    return {
        **{k: getattr(setting, k) for k in setting.__dict__ if not k.startswith("_")},
        "manager_username": rest.username,
    }


@api.post("/restaurants/{slug}/settings/barcode_image", response_model=SettingOut)
async def upload_barcode_image(slug: str, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    setting = db.query(Setting).filter(Setting.restaurant_id == rest.id).first()
    if not setting:
        setting = Setting(restaurant_id=rest.id, company_name=rest.name, currency_1="USD", currency_2="EUR", rate=1.0)
        db.add(setting)
        db.commit()
        db.refresh(setting)

    file_ext = Path(file.filename).suffix
    dest = media_path / f"{rest.slug}_barcode{file_ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    setting.barcode_image_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(setting)
    return {
        **{k: getattr(setting, k) for k in setting.__dict__ if not k.startswith("_")},
        "manager_username": rest.username,
    }


# Categories
@api.get("/restaurants/{slug}/categories", response_model=List[CategoryOut])
def list_categories(slug: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    return db.query(Category).filter(Category.restaurant_id == rest.id).order_by(Category.name.asc()).all()


@api.post("/restaurants/{slug}/categories", response_model=CategoryOut)
def create_category(slug: str, payload: CategoryCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    cat = Category(restaurant_id=rest.id, **payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@api.put("/restaurants/{slug}/categories/{category_id}", response_model=CategoryOut)
def update_category(slug: str, category_id: int, payload: CategoryCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = payload.name
    db.commit()
    db.refresh(cat)
    return cat


@api.delete("/restaurants/{slug}/categories/{category_id}")
def delete_category(slug: str, category_id: int, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    # Prevent deletion if products exist linked
    product_link = db.query(product_categories).filter_by(category_id=category_id).first()
    if product_link:
        raise HTTPException(status_code=400, detail="Cannot delete category with linked products")
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"status": "ok"}


# Ingredients
@api.get("/restaurants/{slug}/ingredients", response_model=List[IngredientOut])
def list_ingredients(slug: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    return db.query(Ingredient).filter(Ingredient.restaurant_id == rest.id).order_by(Ingredient.name.asc()).all()


@api.post("/restaurants/{slug}/ingredients", response_model=IngredientOut)
def create_ingredient(slug: str, payload: IngredientCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    ing = Ingredient(restaurant_id=rest.id, **payload.model_dump())
    db.add(ing)
    db.commit()
    db.refresh(ing)
    return ing


@api.put("/restaurants/{slug}/ingredients/{ingredient_id}", response_model=IngredientOut)
def update_ingredient(slug: str, ingredient_id: int, payload: IngredientCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    ing = db.get(Ingredient, ingredient_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ing.name = payload.name
    db.commit()
    db.refresh(ing)
    return ing


@api.delete("/restaurants/{slug}/ingredients/{ingredient_id}")
def delete_ingredient(slug: str, ingredient_id: int, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    ing = db.get(Ingredient, ingredient_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(ing)
    db.commit()
    return {"status": "ok"}


@api.post("/restaurants/{slug}/ingredients/{ingredient_id}/image", response_model=IngredientOut)
async def upload_ingredient_image(slug: str, ingredient_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    ing = db.get(Ingredient, ingredient_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ext = Path(file.filename).suffix
    dest = media_path / f"{slug}_ingredient_{ingredient_id}{ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    ing.image_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(ing)
    return ing


# Products
@api.get("/restaurants/{slug}/products", response_model=List[ProductOut])
def list_products(slug: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    products = db.query(Product).filter(Product.restaurant_id == rest.id).order_by(Product.name.asc()).all()
    setting = db.query(Setting).filter(Setting.restaurant_id == rest.id).first()
    rate = setting.rate if setting else 1.0
    result: list[dict] = []
    for p in products:
        cat_ids = [r.category_id for r in db.execute(product_categories.select().where(product_categories.c.product_id == p.id)).fetchall()]
        ing_ids = [r.ingredient_id for r in db.execute(product_ingredients.select().where(product_ingredients.c.product_id == p.id)).fetchall()]
        result.append({
            "id": p.id,
            "name": p.name,
            "image_path": p.image_path,
            "price_currency_1": p.price_currency_1,
            "price_currency_2": round(p.price_currency_1 * rate, 2),
            "category_ids": cat_ids,
            "ingredient_ids": ing_ids,
        })
    return result


@api.post("/restaurants/{slug}/products", response_model=ProductOut)
def create_product(slug: str, payload: ProductCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    setting = db.query(Setting).filter(Setting.restaurant_id == rest.id).first()
    rate = setting.rate if setting else 1.0
    product = Product(
        restaurant_id=rest.id,
        name=payload.name,
        price_currency_1=payload.price_currency_1,
    )
    db.add(product)
    db.flush()

    if payload.category_ids:
        for cid in payload.category_ids:
            db.execute(product_categories.insert().values(product_id=product.id, category_id=cid))
    if payload.ingredient_ids:
        for iid in payload.ingredient_ids:
            db.execute(product_ingredients.insert().values(product_id=product.id, ingredient_id=iid))
    db.commit()
    db.refresh(product)
    return {
        "id": product.id,
        "name": product.name,
        "image_path": product.image_path,
        "price_currency_1": product.price_currency_1,
        "price_currency_2": round(product.price_currency_1 * rate, 2),
        "category_ids": payload.category_ids or [],
        "ingredient_ids": payload.ingredient_ids or [],
    }


@api.put("/restaurants/{slug}/products/{product_id}", response_model=ProductOut)
def update_product(slug: str, product_id: int, payload: ProductCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    rest = _get_restaurant_by_slug(db, slug)
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    setting = db.query(Setting).filter(Setting.restaurant_id == rest.id).first()
    rate = setting.rate if setting else 1.0
    product.name = payload.name
    product.price_currency_1 = payload.price_currency_1
    # Reset relations
    db.execute(product_categories.delete().where(product_categories.c.product_id == product_id))
    db.execute(product_ingredients.delete().where(product_ingredients.c.product_id == product_id))
    if payload.category_ids:
        for cid in payload.category_ids:
            db.execute(product_categories.insert().values(product_id=product.id, category_id=cid))
    if payload.ingredient_ids:
        for iid in payload.ingredient_ids:
            db.execute(product_ingredients.insert().values(product_id=product.id, ingredient_id=iid))
    db.commit()
    db.refresh(product)
    return {
        "id": product.id,
        "name": product.name,
        "image_path": product.image_path,
        "price_currency_1": product.price_currency_1,
        "price_currency_2": round(product.price_currency_1 * rate, 2),
        "category_ids": payload.category_ids or [],
        "ingredient_ids": payload.ingredient_ids or [],
    }


@api.delete("/restaurants/{slug}/products/{product_id}")
def delete_product(slug: str, product_id: int, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"status": "ok"}


@api.post("/restaurants/{slug}/categories/{category_id}/image", response_model=CategoryOut)
async def upload_category_image(slug: str, category_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    ext = Path(file.filename).suffix
    dest = media_path / f"{slug}_category_{category_id}{ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    cat.image_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(cat)
    return cat


@api.post("/restaurants/{slug}/products/{product_id}/image", response_model=ProductOut)
async def upload_product_image(slug: str, product_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    _ensure_admin_or_restaurant(principal, slug, db)
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    ext = Path(file.filename).suffix
    dest = media_path / f"{slug}_product_{product_id}{ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    product.image_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(product)
    return product


# Public digital menu endpoint (per restaurant)
@api.get("/public/menu/{restaurant_slug}", response_model=dict)
def public_menu(restaurant_slug: str, db: Session = Depends(get_db)):
    rest = _get_restaurant_by_slug(db, restaurant_slug)
    if not rest.is_active:
        return {"unavailable": True, "message": "Temporarily unavailable"}
    setting = db.query(Setting).filter(Setting.restaurant_id == rest.id).first()
    categories = db.query(Category).filter(Category.restaurant_id == rest.id).order_by(Category.name.asc()).all()
    products = db.query(Product).filter(Product.restaurant_id == rest.id).order_by(Product.name.asc()).all()
    ingredients = db.query(Ingredient).filter(Ingredient.restaurant_id == rest.id).order_by(Ingredient.name.asc()).all()
    # Compose DTO optimized for UI
    cat_map = {c.id: {"id": c.id, "name": c.name, "image_path": c.image_path, "products": []} for c in categories}
    # Link products to categories
    for p in products:
        # find categories via association table
        rows = db.execute(product_categories.select().where(product_categories.c.product_id == p.id)).fetchall()
        p_cat_ids = [r.category_id for r in rows]
        ing_rows = db.execute(product_ingredients.select().where(product_ingredients.c.product_id == p.id)).fetchall()
        p_ing_ids = [r.ingredient_id for r in ing_rows]
        p_ingredients = [i.name for i in ingredients if i.id in p_ing_ids]
        p_dto = {
            "id": p.id,
            "name": p.name,
            "image_path": p.image_path,
            "price_currency_1": p.price_currency_1,
            "price_currency_2": round(p.price_currency_1 * (setting.rate if setting else 1.0), 2),
            "ingredient_names": p_ingredients,
        }
        for cid in p_cat_ids:
            if cid in cat_map:
                cat_map[cid]["products"].append(p_dto)
    return {
        "restaurant": {"name": rest.name, "slug": rest.slug, "logo_image": rest.logo_image},
        "setting": {
            "company_name": setting.company_name if setting else "",
            "logo_path": setting.logo_path if setting else None,
            "currency_1": setting.currency_1 if setting else "USD",
            "currency_2": setting.currency_2 if setting else "EUR",
            "barcode_image_path": setting.barcode_image_path if setting else None,
            "primary_color": setting.primary_color if setting else None,
            "background_color": setting.background_color if setting else None,
        },
        "categories": list(cat_map.values()),
    }


app.mount(settings.api_v1_prefix, api)


