from fastapi import APIRouter,status, HTTPException, Depends
from typing import List
from schemas.orders import Order_create, Order_out, Order_update
from Models.orders import db_create_order, db_get_orders, db_get_orders_by_user, db_get_one_order, db_update_order, db_delete_order
from auth import get_current_user

router = APIRouter()

@router.post("/orders/checkout", response_model=Order_out, status_code=status.HTTP_201_CREATED)
def checkout(order: Order_create, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_order = db_create_order(
        user_id = user_id,
        shipping_address = order.shipping_address
    )
    if not new_order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create order. Cart may be empty.")
    return new_order

@router.get("/orders", response_model=List[Order_out], status_code=status.HTTP_200_OK)
def get_orders(current_user: dict = Depends(get_current_user)):
    orders = db_get_orders_by_user(current_user['id'])
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found")
    return orders

@router.get("/orders/{id}", response_model=Order_out, status_code=status.HTTP_200_OK)
def get_one_order(id: int, current_user: dict = Depends(get_current_user)):
    order = db_get_one_order(id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@router.patch("/orders/{id}", response_model=Order_out, status_code=status.HTTP_202_ACCEPTED)
def update_order(id: int, update_data: Order_update, current_user: dict = Depends(get_current_user)):
    # Drop fields that are None
    update_dict = update_data.dict(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid data provided to update")
        
    order = db_update_order(id, update_dict)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@router.delete("/orders/{id}", status_code=status.HTTP_200_OK)
def delete_order(id: int, current_user: dict = Depends(get_current_user)):
    order = db_delete_order(id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return {"message": "order deleted successfully"}