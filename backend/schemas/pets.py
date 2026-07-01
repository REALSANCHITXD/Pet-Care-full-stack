from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Pets_Create(BaseModel):
    owner_id: int
    name:str
    species:str
    breed : Optional[str]= None
    age :Optional[int] =None
    medical_history:Optional[str] = None
    
class Pets_Out(BaseModel):
    owner_id: int
    name:str
    species:str
    breed : Optional[str]= None
    age :Optional[int] =None
    medical_history:Optional[str] = None
    id :int
    created_at : datetime

class Pets_Update(BaseModel):
    name:Optional[str] = None
    species:Optional[str] =None
    breed : Optional[str]= None
    age :Optional[int] =None
    medical_history:Optional[str] = None

