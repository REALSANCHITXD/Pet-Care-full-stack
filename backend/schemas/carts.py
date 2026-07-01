from datetime import datetime
from pydantic import BaseModel
from typing import Optional,List



class add_cart(BaseModel):
    product_id :int
    quantity: int = 1

class single_item_return(BaseModel):
    id:int
    cart_id:int
    product_id:int
    quantity:int
    product_name:Optional[str]=None
    price:Optional[float]=None
    subtotal:Optional[float]=None

class returning_whole_cart(BaseModel):
    id:int
    user_id:int
    items:List[single_item_return] = []
    total_amount:float = 0.0