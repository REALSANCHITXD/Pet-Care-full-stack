from pydantic import computed_field
from datetime import datetime
from pydantic import BaseModel
from typing import Optional,List
from enum import Enum

class order_status(str,Enum):
    pending ="pending"
    out_for_delivery = "out for delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class Order_create(BaseModel):
    shipping_address :str 
    
class return_order(BaseModel):
    id: int
    product_id :int
    quantity: int=1
    price_at_purchase : float = 0.0
    order_id : int
    @computed_field
    @property
    def subtotal(self) -> float:
        return self.quantity * self.price_at_purchase

class Order_out(Order_create):
    id: int
    status: str
    created_at: datetime
    total_amount: float
    items: List[return_order] = []    

class Order_update(BaseModel):
    status: Optional[str] = None
    


