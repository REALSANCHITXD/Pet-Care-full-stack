from fastapi import APIRouter,status,HTTPException, Depends
from typing import List
from Models.vets import db_create_vet,db_delete_vet,db_get_all_vet,db_get_one_vet,db_update_vet,db_filter_rating_vet,db_filter_vets,db_filter_vets_by_proximity
from schemas.vets import Vets_Create,Vets_Out,Vets_Update
from auth import get_current_user

router = APIRouter()

@router.post("/vets",response_model=Vets_Out,status_code=status.HTTP_201_CREATED)
def create_vet(vets:Vets_Create, current_user: str = Depends(get_current_user)):
    new_vet=db_create_vet(
        name = vets.name,
        specialties=vets.specialties,
        clinic_name=vets.clinic_name,
        address=vets.address,
        latitude=vets.latitude,
        longitude=vets.longitude,
        rating=vets.rating
        
    )
    if not new_vet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"vet with {vets.name} is not created")
    return new_vet

@router.get("/vets",response_model=List[Vets_Out],status_code=status.HTTP_202_ACCEPTED)
def get_all_vets(skip: int = 0, limit: int = 20):
    return db_get_all_vet(skip, limit)

@router.get("/vets/{id}",response_model=Vets_Out,status_code=status.HTTP_200_OK)
def get_one_vet(id:int, current_user: str = Depends(get_current_user)):
    vet = db_get_one_vet(id)
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"vet with {id} is not found")
    return vet

@router.patch("/vets/{id}",response_model=Vets_Out,status_code=status.HTTP_202_ACCEPTED)
def update_vet(id:int,vet_update:Vets_Update, current_user: str = Depends(get_current_user)):
    vet = db_update_vet(id,vet_update.dict(exclude_unset=True))
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"vet with {id} is not found")
    return vet

@router.delete("/vets/{id}",status_code=status.HTTP_200_OK)
def delete_vet(id:int, current_user: str = Depends(get_current_user)):
    vet = db_delete_vet(id)
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"vet with {id} is not found")
    return {"message": "vet deleted successfully"}

@router.get("/vets/search/specialties",response_model=List[Vets_Out],status_code=status.HTTP_200_OK)
def filter_vets(specialties:str,clinic_name:str):
    return db_filter_vets(specialties,clinic_name)

@router.get("/vets/search/rating",response_model=List[Vets_Out],status_code=status.HTTP_200_OK)
def filter_rating_vet(rating:str,clinic_name:str):
    return db_filter_rating_vet(rating,clinic_name)

@router.get("/vets/search/proximity", status_code=status.HTTP_200_OK)
def search_vets_by_proximity(lat: float, lng: float, limit: int = 10):
    vets = db_filter_vets_by_proximity(lat, lng, limit)
    if not vets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No vets found nearby")
    return vets