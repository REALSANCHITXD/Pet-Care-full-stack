from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Optional
from sqlmodel import Session

from database import get_db
from auth import get_current_user
from Models.products import (
    ProductCreate, ProductUpdate, ProductOut, ProductFilter,
    db_create_product, db_get_all_products, db_get_one_product,
    db_update_product, db_delete_product, db_filter_products
)

router = APIRouter(prefix="/products")

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_create_product(db, product_data)

@router.get("/", response_model=List[ProductOut], status_code=status.HTTP_200_OK)
def get_all_products(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db_get_all_products(db, skip, limit) or []

@router.get("/search", response_model=List[ProductOut], status_code=status.HTTP_200_OK)
def filter_products(
    category: Optional[str] = None,
    price_up: Optional[float] = None,
    price_down: Optional[float] = None,
    rating: Optional[float] = None,
    db: Session = Depends(get_db)
):
    products = db_filter_products(db, category, price_up, price_down, rating)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    return products

@router.get("/{id}", response_model=ProductOut, status_code=status.HTTP_200_OK)
def get_one_product(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    product = db_get_one_product(db, id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.patch("/{id}", response_model=ProductOut, status_code=status.HTTP_202_ACCEPTED)
def update_product(id: int, product_update: ProductUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    product = db_update_product(db, id, product_update)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    product = db_delete_product(db, id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"message": "product deleted successfully"}