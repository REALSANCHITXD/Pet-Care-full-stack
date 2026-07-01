from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Booking_create(BaseModel):
    user_id : int
    vet_id :int
    appointment_time  : datetime   
    reason : Optional[str] = None

class Booking_out(Booking_create):
    id: int
    status :str
    created_at : datetime

class Booking_update(BaseModel):
    status : Optional[str]=None
    appointment_time  : Optional[datetime]
    reason : Optional[str] = None    