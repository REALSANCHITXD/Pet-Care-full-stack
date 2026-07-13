from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlmodel import Session

from database import get_db
from auth import get_current_user
from Models.vets import (
    VetCreate, VetUpdate, VetOut,
    db_create_vet, db_get_all_vet, db_get_one_vet, db_update_vet,
    db_delete_vet, db_filter_vets, db_filter_rating_vet, db_filter_vets_by_proximity
)

router = APIRouter()

@router.post("/vets", response_model=VetOut, status_code=status.HTTP_201_CREATED)
def create_vet(vet_data: VetCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_create_vet(db, vet_data)

@router.get("/vets", response_model=List[VetOut], status_code=status.HTTP_202_ACCEPTED)
def get_all_vets(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db_get_all_vet(db, skip, limit)

@router.get("/vets/search/specialties", response_model=List[VetOut], status_code=status.HTTP_200_OK)
def filter_vets(specialties: str, clinic_name: str, db: Session = Depends(get_db)):
    return db_filter_vets(db, specialties, clinic_name)

@router.get("/vets/search/rating", response_model=List[VetOut], status_code=status.HTTP_200_OK)
def filter_rating_vet(rating: float, clinic_name: str, db: Session = Depends(get_db)):
    return db_filter_rating_vet(db, rating, clinic_name)

@router.get("/vets/search/proximity", status_code=status.HTTP_200_OK)
def search_vets_by_proximity(lat: float, lng: float, limit: int = 10, db: Session = Depends(get_db)):
    vets = db_filter_vets_by_proximity(db, lat, lng, limit)
    if not vets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No vets found nearby")
    return vets

@router.get("/vets/{id}", response_model=VetOut, status_code=status.HTTP_200_OK)
def get_one_vet(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    vet = db_get_one_vet(db, id)
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vet with id {id} not found")
    return vet

@router.patch("/vets/{id}", response_model=VetOut, status_code=status.HTTP_202_ACCEPTED)
def update_vet(id: int, vet_update: VetUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    vet = db_update_vet(db, id, vet_update)
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vet with id {id} not found")
    return vet

@router.delete("/vets/{id}", status_code=status.HTTP_200_OK)
def delete_vet(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    vet = db_delete_vet(db, id)
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vet with id {id} not found")
    return {"message": "vet deleted successfully"}