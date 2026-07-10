from pydantic_core import ErrorDetails
from fastapi import APIRouter,status,HTTPException, Depends
from typing import List
from Models.booking import db_booking_create,db_booking_delete,db_booking_get_all,db_booking_get_one,db_booking_update,db_booking_get_by_user
from schemas.booking import Booking_create, Booking_out, Booking_update
from auth import get_current_user

router=APIRouter()

@router.get("/bookings",response_model = List[Booking_out],status_code = status.HTTP_200_OK)
def get_bookings(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    all_bookings = db_booking_get_by_user(user_id)
    if not all_bookings:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = "There is nothing in the database.")
    return all_bookings

@router.get("/bookings/{id}",response_model = Booking_out ,status_code =status.HTTP_200_OK)
def get_booking_one(id:int, current_user: str = Depends(get_current_user)):
    one_booking = db_booking_get_one(id)
    if not one_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f"The {id} u are searching is not there")
    return one_booking

@router.post("/bookings",response_model = Booking_out,status_code = status.HTTP_201_CREATED)
def booking_create(booking_create:Booking_create, current_user: str = Depends(get_current_user)):
    new_booking=db_booking_create(
        user_id=booking_create.user_id,
        vet_id=booking_create.vet_id,
        appointment_time=booking_create.appointment_time,
        reason=booking_create.reason
    )
    if not new_booking:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail = f"booking could not be created. The vet might already be booked at this time.")
    return new_booking

@router.patch("/bookings/{id}",response_model = Booking_out,status_code=status.HTTP_202_ACCEPTED)
def booking_update(id:int ,booking_update:Booking_update, current_user: str = Depends(get_current_user)):
    booking = db_booking_update(id,booking_update.dict(exclude_unset=True))
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f"booking with id {id} is not found")
    return booking

@router.delete("/bookings/{id}",status_code=status.HTTP_200_OK)
def booking_delete(id:int, current_user: str = Depends(get_current_user)):
    booking = db_booking_delete(id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f"booking with id {id} is not found")
    return {"message":"booking deleted successfully"}