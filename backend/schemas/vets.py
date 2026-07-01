from datetime import datetime
from typing import Optional
from pydantic import BaseModel



class Vets_Create(BaseModel):
    name: str
    clinic_name: str
    address: str
    latitude: float                    
    longitude: float                    
    specialties: Optional[str] = None
    rating: Optional[float] = None

    
class Vets_Out(Vets_Create):
    id: int
    created_at: datetime

class Vets_Update(BaseModel):
    name: Optional[str]=None
    clinic_name: Optional[str]=None
    address: Optional[str]=None
    latitude: Optional[float]=None
    longitude: Optional[float]=None
    specialties: Optional[str]=None
    rating: Optional[float]=None
