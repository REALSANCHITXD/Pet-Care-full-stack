from typing import Optional, List
from sqlmodel import SQLModel, Field, Session, select


# --- Table Models (DB) ---
class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)

class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="carts.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = 1


# --- Request Schemas ---
class AddCart(SQLModel):
    product_id: int
    quantity: int = 1


# --- Response Schemas ---
class CartItemOut(SQLModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int
    product_name: Optional[str] = None
    price: Optional[float] = None
    subtotal: Optional[float] = None

class CartOut(SQLModel):
    id: int
    user_id: int
    items: List[CartItemOut] = []
    total_amount: float = 0.0


# --- CRUD Functions ---
def db_get_or_create_cart(session: Session, user_id: int) -> Cart:
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart

def db_add_cart_item(session: Session, cart_id: int, product_id: int, quantity: int) -> CartItem:
    existing = session.exec(
        select(CartItem).where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
    ).first()
    if existing:
        existing.quantity += quantity
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def db_get_cart_items(session: Session, cart_id: int) -> List[CartItemOut]:
    from Models.products import Product
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart_id)).all()
    result = []
    for item in items:
        product = session.get(Product, item.product_id)
        subtotal = item.quantity * product.price if product else 0.0
        result.append(CartItemOut(
            id=item.id,
            cart_id=item.cart_id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_name=product.name if product else None,
            price=product.price if product else None,
            subtotal=subtotal,
        ))
    return result

def db_remove_cart_item(session: Session, item_id: int):
    item = session.get(CartItem, item_id)
    if not item:
        return None
    session.delete(item)
    session.commit()
    return item

def db_delete_cart(session: Session, cart_id: int):
    cart = session.get(Cart, cart_id)
    if not cart:
        return None
    session.delete(cart)
    session.commit()
    return cart
