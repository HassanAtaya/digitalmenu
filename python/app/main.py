from pathlib import Path
from typing import List
from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .core.config import settings
from .core.database import Base, engine, get_db
from .core.security import create_access_token, verify_password, get_password_hash
from .dependencies import get_current_user
from .models.models import User, Setting, Category, Product, Ingredient, product_categories, product_ingredients
from .schemas.schemas import (
    Token,
    UserOut,
    SettingOut,
    SettingCreate,
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


api = FastAPI()


@api.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}


# Settings
@api.get("/settings", response_model=SettingOut)
def get_settings(db: Session = Depends(get_db)):
    setting = db.query(Setting).order_by(Setting.id.asc()).first()
    if not setting:
        setting = Setting(company_name="", currency_1="USD", currency_2="EUR", rate=1.0)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


@api.post("/settings", response_model=SettingOut)
def save_settings(payload: SettingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    setting = db.query(Setting).order_by(Setting.id.asc()).first()
    if not setting:
        setting = Setting(**payload.model_dump())
        db.add(setting)
    else:
        data = payload.model_dump()
        for k, v in data.items():
            setattr(setting, k, v)
    db.commit()
    db.refresh(setting)
    return setting


@api.post("/settings/logo", response_model=SettingOut)
async def upload_logo(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    setting = db.query(Setting).order_by(Setting.id.asc()).first()
    if not setting:
        setting = Setting(company_name="", currency_1="USD", currency_2="EUR", rate=1.0)
        db.add(setting)
        db.commit()
        db.refresh(setting)

    file_ext = Path(file.filename).suffix
    dest = media_path / f"logo{file_ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    setting.logo_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(setting)
    return setting


@api.post("/settings/barcode_image", response_model=SettingOut)
async def upload_barcode_image(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    setting = db.query(Setting).order_by(Setting.id.asc()).first()
    if not setting:
        setting = Setting(company_name="", currency_1="USD", currency_2="EUR", rate=1.0)
        db.add(setting)
        db.commit()
        db.refresh(setting)

    file_ext = Path(file.filename).suffix
    dest = media_path / f"barcode{file_ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    setting.barcode_image_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(setting)
    return setting


# Categories
@api.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name.asc()).all()


@api.post("/categories", response_model=CategoryOut)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = Category(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@api.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = payload.name
    db.commit()
    db.refresh(cat)
    return cat


@api.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
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
@api.get("/ingredients", response_model=List[IngredientOut])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(Ingredient).order_by(Ingredient.name.asc()).all()


@api.post("/ingredients", response_model=IngredientOut)
def create_ingredient(payload: IngredientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ing = Ingredient(**payload.model_dump())
    db.add(ing)
    db.commit()
    db.refresh(ing)
    return ing


@api.put("/ingredients/{ingredient_id}", response_model=IngredientOut)
def update_ingredient(ingredient_id: int, payload: IngredientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ing = db.get(Ingredient, ingredient_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ing.name = payload.name
    db.commit()
    db.refresh(ing)
    return ing


@api.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ing = db.get(Ingredient, ingredient_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(ing)
    db.commit()
    return {"status": "ok"}


@api.post("/ingredients/{ingredient_id}/image", response_model=IngredientOut)
async def upload_ingredient_image(ingredient_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ing = db.get(Ingredient, ingredient_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ext = Path(file.filename).suffix
    dest = media_path / f"ingredient_{ingredient_id}{ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    ing.image_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(ing)
    return ing


# Products
@api.get("/products", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.name.asc()).all()
    result: list[dict] = []
    for p in products:
        cat_ids = [r.category_id for r in db.execute(product_categories.select().where(product_categories.c.product_id == p.id)).fetchall()]
        ing_ids = [r.ingredient_id for r in db.execute(product_ingredients.select().where(product_ingredients.c.product_id == p.id)).fetchall()]
        result.append({
            "id": p.id,
            "name": p.name,
            "image_path": p.image_path,
            "price_currency_1": p.price_currency_1,
            "price_currency_2": p.price_currency_2,
            "category_ids": cat_ids,
            "ingredient_ids": ing_ids,
        })
    return result


@api.post("/products", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    setting = db.query(Setting).order_by(Setting.id.asc()).first()
    rate = setting.rate if setting else 1.0
    product = Product(
        name=payload.name,
        price_currency_1=payload.price_currency_1,
        price_currency_2=round(payload.price_currency_1 * rate, 2),
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
        "price_currency_2": product.price_currency_2,
        "category_ids": payload.category_ids or [],
        "ingredient_ids": payload.ingredient_ids or [],
    }


@api.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    setting = db.query(Setting).order_by(Setting.id.asc()).first()
    rate = setting.rate if setting else 1.0
    product.name = payload.name
    product.price_currency_1 = payload.price_currency_1
    product.price_currency_2 = round(payload.price_currency_1 * rate, 2)
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
        "price_currency_2": product.price_currency_2,
        "category_ids": payload.category_ids or [],
        "ingredient_ids": payload.ingredient_ids or [],
    }


@api.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"status": "ok"}


@api.post("/categories/{category_id}/image", response_model=CategoryOut)
async def upload_category_image(category_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    ext = Path(file.filename).suffix
    dest = media_path / f"category_{category_id}{ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    cat.image_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(cat)
    return cat


@api.post("/products/{product_id}/image", response_model=ProductOut)
async def upload_product_image(product_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    ext = Path(file.filename).suffix
    dest = media_path / f"product_{product_id}{ext}"
    with dest.open("wb") as f:
        f.write(await file.read())
    base = str(request.base_url).rstrip('/')
    product.image_path = f"{base}/media/{dest.name}"
    db.commit()
    db.refresh(product)
    return product


# Public digital menu endpoint
@api.get("/digital_menu", response_model=dict)
def public_menu(db: Session = Depends(get_db)):
    setting = db.query(Setting).order_by(Setting.id.asc()).first()
    categories = db.query(Category).order_by(Category.name.asc()).all()
    products = db.query(Product).order_by(Product.name.asc()).all()
    ingredients = db.query(Ingredient).order_by(Ingredient.name.asc()).all()
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
            "price_currency_2": p.price_currency_2,
            "ingredient_names": p_ingredients,
        }
        for cid in p_cat_ids:
            if cid in cat_map:
                cat_map[cid]["products"].append(p_dto)
    return {
        "setting": {
            "company_name": setting.company_name if setting else "",
            "logo_path": setting.logo_path if setting else None,
            "currency_1": setting.currency_1 if setting else "USD",
            "currency_2": setting.currency_2 if setting else "EUR",
            "barcode_image_path": setting.barcode_image_path if setting else None,
        },
        "categories": list(cat_map.values()),
    }


app.mount(settings.api_v1_prefix, api)


