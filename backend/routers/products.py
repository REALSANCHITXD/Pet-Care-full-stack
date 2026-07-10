from fastapi import APIRouter,status,HTTPException,Depends  
from typing import List , Optional
from schemas.products import Products_Create,Products_Out,Products_Update,Product_filtering
from Models.products import db_create_product,db_get_all_products,db_get_one_product,db_update_product,db_delete_product,db_filter_products
from auth import get_current_user

router = APIRouter(
    prefix = "/products"
)

@router.post("/",response_model=Products_Out, status_code=status.HTTP_201_CREATED)
def create_product(products_create : Products_Create, current_user: str = Depends(get_current_user)):
    new_product = db_create_product(**products_create.model_dump())

    if not new_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="product not created")
    return new_product

@router.get("/",response_model=List[Products_Out], status_code=status.HTTP_200_OK)
def get_all_products(skip: int = 0, limit: int = 20):
    products = db_get_all_products(skip, limit)
    return products or []

@router.get("/search",response_model=List[Products_Out], status_code=status.HTTP_200_OK)
def filter_products(filtering: Product_filtering = Depends()):
    products = db_filter_products(**filtering.model_dump())
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    return products

@router.get("/{id}",response_model=Products_Out, status_code=status.HTTP_200_OK)
def get_one_product(id:int, current_user: str = Depends(get_current_user)):
    product = db_get_one_product(id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    return product

@router.patch("/{id}",response_model=Products_Out, status_code=status.HTTP_202_ACCEPTED)
def update_product(id:int, product_update:Products_Update, current_user: str = Depends(get_current_user)):
    product = db_update_product(id, product_update.model_dump(exclude_unset=True))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    return product

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product(id:int, current_user: str = Depends(get_current_user)):
    product = db_delete_product(id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")
    return {"message": "product deleted successfully"}