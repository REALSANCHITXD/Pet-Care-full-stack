from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlmodel import Session

from database import get_db
from auth import get_current_user
from Models.pets import PetCreate, PetUpdate, PetOut, db_create_pets, db_get_all_pets, db_get_one_pet, db_update_pets, db_delete_pet

router = APIRouter()

@router.post("/pets", response_model=PetOut, status_code=status.HTTP_201_CREATED)
def create_pet(pet_data: PetCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_create_pets(db, pet_data)

@router.get("/pets", response_model=List[PetOut], status_code=status.HTTP_200_OK)
def get_pets(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_get_all_pets(db)

@router.get("/pets/{id}", response_model=PetOut, status_code=status.HTTP_200_OK)
def get_pet_one(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    pet = db_get_one_pet(db, id)
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pet with id {id} not found")
    return pet

@router.patch("/pets/{id}", response_model=PetOut, status_code=status.HTTP_202_ACCEPTED)
def pet_update(id: int, pet_update: PetUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    pet = db_update_pets(db, id, pet_update)
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pet with id {id} not found")
    return pet

@router.delete("/pets/{id}", status_code=status.HTTP_200_OK)
def delete_pet(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    pet = db_delete_pet(db, id)
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pet with id {id} not found")
    return {"message": "pet deleted successfully"}