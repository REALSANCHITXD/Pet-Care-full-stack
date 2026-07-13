from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlmodel import Session

from database import get_db
from auth import get_current_user
from Models.booking import (
    BookingCreate, BookingUpdate, BookingOut,
    db_booking_create, db_booking_get_all, db_booking_get_by_user,
    db_booking_get_one, db_booking_update, db_booking_delete
)

router = APIRouter()

@router.get("/bookings", response_model=List[BookingOut], status_code=status.HTTP_200_OK)
def get_bookings(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = db_booking_get_by_user(db, current_user.id)
    if not bookings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bookings found")
    return bookings

@router.get("/bookings/{id}", response_model=BookingOut, status_code=status.HTTP_200_OK)
def get_booking_one(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db_booking_get_one(db, id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with id {id} not found")
    return booking

@router.post("/bookings", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def booking_create(booking_data: BookingCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    new_booking = db_booking_create(db, booking_data)
    if not new_booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking could not be created. The vet might already be booked at this time.")
    return new_booking

@router.patch("/bookings/{id}", response_model=BookingOut, status_code=status.HTTP_202_ACCEPTED)
def booking_update(id: int, booking_update: BookingUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db_booking_update(db, id, booking_update)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with id {id} not found")
    return booking

@router.delete("/bookings/{id}", status_code=status.HTTP_200_OK)
def booking_delete(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db_booking_delete(db, id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with id {id} not found")
    return {"message": "booking deleted successfully"}