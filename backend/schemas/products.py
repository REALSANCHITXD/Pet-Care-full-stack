from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Products_Create(BaseModel):
    name: str
    description: Optional[str]=None
    price: float
    stock: int = 1
    category: Optional[str] = None
    rating: Optional[float] = None

class Products_Out(Products_Create):
    id: int
    created_at: datetime

class Products_Update(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    rating: Optional[float] = None

class Product_filtering(BaseModel):
    category:Optional[str]=None
    price_up:Optional[float]=None
    price_down:Optional[float]=None
    rating:Optional[float]=None