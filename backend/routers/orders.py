from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlmodel import Session

from database import get_db
from auth import get_current_user
from Models.orders import (
    OrderCreate, OrderUpdate, OrderOut, OrderItemOut,
    db_create_order, db_get_orders, db_get_orders_by_user,
    db_get_one_order, db_update_order, db_delete_order, db_mark_order_paid
)

router = APIRouter()

def _build_order_out(order_tuple) -> OrderOut:
    order, items = order_tuple
    return OrderOut(
        id=order.id,
        shipping_address=order.shipping_address,
        status=order.status,
        created_at=order.created_at,
        total_amount=order.total_amount,
        items=[OrderItemOut(**item.model_dump()) for item in items]
    )

@router.post("/orders/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout(order: OrderCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = db_create_order(db, current_user.id, order)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create order. Cart may be empty.")
    return _build_order_out(result)

@router.get("/orders", response_model=List[OrderOut], status_code=status.HTTP_200_OK)
def get_orders(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    results = db_get_orders_by_user(db, current_user.id)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found")
    return [_build_order_out(r) for r in results]

@router.get("/orders/{id}", response_model=OrderOut, status_code=status.HTTP_200_OK)
def get_one_order(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = db_get_one_order(db, id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return _build_order_out(result)

@router.patch("/orders/{id}", response_model=OrderOut, status_code=status.HTTP_202_ACCEPTED)
def update_order(id: int, update_data: OrderUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = db_update_order(db, id, update_data)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return _build_order_out(result)

@router.delete("/orders/{id}", status_code=status.HTTP_200_OK)
def delete_order(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = db_delete_order(db, id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return {"message": "order deleted successfully"}

@router.post("/orders/{id}/pay", response_model=OrderOut, status_code=status.HTTP_200_OK)
def pay_order(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = db_get_one_order(db, id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order, _ = result
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    paid = db_mark_order_paid(db, id)
    return _build_order_out(paid)