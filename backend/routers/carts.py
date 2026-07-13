from fastapi import APIRouter, status, HTTPException, Depends
from sqlmodel import Session

from database import get_db
from auth import get_current_user
from Models.carts import AddCart, CartOut, db_get_or_create_cart, db_add_cart_item, db_get_cart_items, db_remove_cart_item

router = APIRouter()

@router.post("/cart", status_code=status.HTTP_201_CREATED)
def add_to_cart(item: AddCart, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db_get_or_create_cart(db, current_user.id)
    cart_item = db_add_cart_item(db, cart.id, item.product_id, item.quantity)
    if not cart_item:
        raise HTTPException(status_code=500, detail="Failed to add item to cart")
    return cart_item

@router.get("/cart", response_model=CartOut, status_code=status.HTTP_200_OK)
def get_cart(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db_get_or_create_cart(db, current_user.id)
    items = db_get_cart_items(db, cart.id)
    total_amount = sum(item.subtotal for item in items if item.subtotal)
    return CartOut(id=cart.id, user_id=current_user.id, items=items, total_amount=total_amount)

@router.delete("/cart/items/{id}", status_code=status.HTTP_200_OK)
def remove_from_cart(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = db_remove_cart_item(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item removed from cart"}
