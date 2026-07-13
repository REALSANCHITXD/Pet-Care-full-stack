from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select


# --- Table Model (DB) ---
class Booking(SQLModel, table=True):
    __tablename__ = "bookings"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    vet_id: int = Field(foreign_key="vets.id")
    appointment_time: datetime
    reason: Optional[str] = None
    status: str = Field(default="pending")
    created_at: Optional[datetime] = Field(default=None)


# --- Request Schemas ---
class BookingCreate(SQLModel):
    user_id: int
    vet_id: int
    appointment_time: datetime
    reason: Optional[str] = None

class BookingUpdate(SQLModel):
    status: Optional[str] = None
    appointment_time: Optional[datetime] = None
    reason: Optional[str] = None


# --- Response Schema ---
class BookingOut(SQLModel):
    id: int
    user_id: int
    vet_id: int
    appointment_time: datetime
    reason: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None


# --- CRUD Functions ---
def db_booking_create(session: Session, data: BookingCreate):
    # Check for collision
    collision = session.exec(
        select(Booking).where(
            Booking.vet_id == data.vet_id,
            Booking.appointment_time == data.appointment_time
        )
    ).first()
    if collision:
        return None

    booking = Booking(**data.model_dump())
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking

def db_booking_get_by_user(session: Session, user_id: int):
    return session.exec(select(Booking).where(Booking.user_id == user_id)).all()

def db_booking_get_all(session: Session):
    return session.exec(select(Booking)).all()

def db_booking_get_one(session: Session, id: int):
    return session.get(Booking, id)

def db_booking_update(session: Session, id: int, data: BookingUpdate):
    booking = session.get(Booking, id)
    if not booking:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(booking, key, value)
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking

def db_booking_delete(session: Session, id: int):
    booking = session.get(Booking, id)
    if not booking:
        return None
    session.delete(booking)
    session.commit()
    return booking