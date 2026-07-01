from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from Models.pets import db_create_pets,db_delete_pet,db_get_all_pets,db_get_one_pet,db_update_pets
from schemas.pets import Pets_Create, Pets_Out, Pets_Update
from auth import get_current_user

router = APIRouter()

@router.post("/pets",response_model=Pets_Out,status_code=status.HTTP_201_CREATED)
def create_pet(Pets_Create:Pets_Create, current_user: str = Depends(get_current_user)):
    new_pet = db_create_pets(
        owner_id=Pets_Create.owner_id,
        name=Pets_Create.name,
        species=Pets_Create.species,
        breed=Pets_Create.breed,
        age=Pets_Create.age,
        medical_history=Pets_Create.medical_history
    )
    if not new_pet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"pet could not be created")
    return new_pet

@router.get("/pets",response_model=List[Pets_Out],status_code=status.HTTP_200_OK)
def get_pets(current_user: str = Depends(get_current_user)):
    return db_get_all_pets()

@router.get("/pets/{id}",response_model=Pets_Out,status_code=status.HTTP_200_OK)
def get_pet_one(id:int, current_user: str = Depends(get_current_user)):
    pet = db_get_one_pet(id)
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"pet with {id} is not found")
    return pet

@router.patch("/pets/{id}",response_model=Pets_Out,status_code=status.HTTP_202_ACCEPTED)
def pet_update(id:int,pet_update:Pets_Update, current_user: str = Depends(get_current_user)):
    pet = db_update_pets(id,pet_update.dict(exclude_unset=True))
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"pet with {id} is not found")
    return pet

@router.delete("/pets/{id}",status_code=status.HTTP_200_OK)
def delete_pet(id:int, current_user: str = Depends(get_current_user)):
    pet = db_delete_pet(id)
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"pet with {id} is not found")
    return {"message":"pet deleted successfully"}