from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select, or_


# --- Table Model (DB) ---
class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 1
    category: Optional[str] = None
    rating: Optional[float] = None
    created_at: Optional[datetime] = Field(default=None)


# --- Request Schemas ---
class ProductCreate(SQLModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 1
    category: Optional[str] = None
    rating: Optional[float] = None

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    rating: Optional[float] = None

class ProductFilter(SQLModel):
    category: Optional[str] = None
    price_up: Optional[float] = None
    price_down: Optional[float] = None
    rating: Optional[float] = None


# --- Response Schema ---
class ProductOut(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None
    rating: Optional[float] = None
    created_at: Optional[datetime] = None


# --- CRUD Functions ---
def db_create_product(session: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

def db_get_all_products(session: Session, skip: int = 0, limit: int = 20):
    return session.exec(select(Product).offset(skip).limit(limit)).all()

def db_get_one_product(session: Session, id: int):
    return session.get(Product, id)

def db_update_product(session: Session, id: int, data: ProductUpdate):
    product = session.get(Product, id)
    if not product:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

def db_delete_product(session: Session, id: int):
    product = session.get(Product, id)
    if not product:
        return None
    session.delete(product)
    session.commit()
    return product

def db_filter_products(session: Session, category: str = None, price_up: float = None, price_down: float = None, rating: float = None):
    query = select(Product)
    if category:
        query = query.where(Product.category == category)
    if price_up:
        query = query.where(Product.price <= price_up)
    if price_down:
        query = query.where(Product.price >= price_down)
    if rating:
        query = query.where(Product.rating == rating)
    return session.exec(query).all()