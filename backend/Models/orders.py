from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Session, select
from pydantic import computed_field


# --- Enums ---
class OrderStatus(str, Enum):
    pending = "pending"
    out_for_delivery = "out for delivery"
    delivered = "delivered"
    cancelled = "cancelled"


# --- Table Models (DB) ---
class Order(SQLModel, table=True):
    __tablename__ = "orders"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    shipping_address: str
    total_amount: float = 0.0
    status: str = Field(default=OrderStatus.pending)
    created_at: Optional[datetime] = Field(default=None)

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = 1
    price_at_purchase: float = 0.0


# --- Request Schemas ---
class OrderCreate(SQLModel):
    shipping_address: str

class OrderUpdate(SQLModel):
    status: Optional[str] = None


# --- Response Schemas ---
class OrderItemOut(SQLModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float
    order_id: int

    @computed_field
    @property
    def subtotal(self) -> float:
        return self.quantity * self.price_at_purchase

class OrderOut(SQLModel):
    id: int
    shipping_address: str
    status: str
    created_at: Optional[datetime] = None
    total_amount: float
    items: List[OrderItemOut] = []


# --- CRUD Functions ---
def db_get_order_items(session: Session, order_id: int):
    return session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()

def db_create_order(session: Session, user_id: int, data: OrderCreate):
    from Models.carts import Cart, CartItem
    from Models.products import Product

    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        return None

    cart_items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    if not cart_items:
        return None

    total_amount = 0.0
    for ci in cart_items:
        product = session.get(Product, ci.product_id)
        if product:
            total_amount += ci.quantity * product.price

    order = Order(user_id=user_id, shipping_address=data.shipping_address, total_amount=total_amount)
    session.add(order)
    session.flush()  # get order.id before committing

    for ci in cart_items:
        product = session.get(Product, ci.product_id)
        if product:
            item = OrderItem(order_id=order.id, product_id=ci.product_id, quantity=ci.quantity, price_at_purchase=product.price)
            session.add(item)
            product.stock = max(product.stock - ci.quantity, 0)
            session.add(product)

    session.delete(cart)
    session.commit()
    session.refresh(order)
    order_items = db_get_order_items(session, order.id)
    return order, order_items

def db_get_orders(session: Session):
    orders = session.exec(select(Order)).all()
    return [(o, db_get_order_items(session, o.id)) for o in orders]

def db_get_orders_by_user(session: Session, user_id: int):
    orders = session.exec(select(Order).where(Order.user_id == user_id).order_by(Order.id.desc())).all()
    return [(o, db_get_order_items(session, o.id)) for o in orders]

def db_get_one_order(session: Session, id: int):
    order = session.get(Order, id)
    if not order:
        return None
    return order, db_get_order_items(session, order.id)

def db_update_order(session: Session, id: int, data: OrderUpdate):
    order = session.get(Order, id)
    if not order:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(order, key, value)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order, db_get_order_items(session, order.id)

def db_delete_order(session: Session, id: int):
    order = session.get(Order, id)
    if not order:
        return None
    session.delete(order)
    session.commit()
    return order

def db_mark_order_paid(session: Session, id: int):
    order = session.get(Order, id)
    if not order:
        return None
    order.status = "paid"
    session.add(order)
    session.commit()
    session.refresh(order)
    return order, db_get_order_items(session, order.id)
