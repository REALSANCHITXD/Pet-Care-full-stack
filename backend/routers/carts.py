from fastapi import APIRouter, status, HTTPException, Depends
from schemas.carts import add_cart, returning_whole_cart
from Models.carts import (
    db_get_or_create_cart, 
    db_add_cart_item, 
    db_get_cart_items, 
    db_remove_cart_item,
    db_delete_cart
)
from auth import get_current_user

router = APIRouter()

@router.post("/cart", status_code=status.HTTP_201_CREATED)
def add_to_cart(item: add_cart, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    cart = db_get_or_create_cart(user_id)
    cart_item = db_add_cart_item(cart['id'], item.product_id, item.quantity)
    
    if not cart_item:
        raise HTTPException(status_code=500, detail="Failed to add item to cart")
        
    return cart_item

@router.get("/cart", response_model=returning_whole_cart, status_code=status.HTTP_200_OK)
def get_cart(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    cart = db_get_or_create_cart(user_id)
    items = db_get_cart_items(cart['id'])
    
    total_amount = sum(item['subtotal'] for item in items if item['subtotal'])
    
    return {
        "id": cart['id'],
        "user_id": user_id,
        "items": items,
        "total_amount": total_amount
    }

@router.delete("/cart/items/{id}", status_code=status.HTTP_200_OK)
def remove_from_cart(id: int, current_user: dict = Depends(get_current_user)):
    # Note: ideally you would check if the cart item belongs to the user
    deleted = db_remove_cart_item(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item removed from cart"}
