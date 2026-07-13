from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from sqlmodel import Session

from database import get_db
from auth import get_current_user
from Models.Users import (
    UserCreate, UserUpdate, UserOut,
    db_create_user, db_get_users, db_get_one_user, db_update_user, db_delete_user
)

router = APIRouter()

@router.post('/users', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return db_create_user(db, user_data)

@router.get("/users", response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_users(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_get_users(db)

@router.get("/users/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.get("/users/{id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_one_user(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db_get_one_user(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    return user

@router.patch("/users/{id}", response_model=UserOut, status_code=status.HTTP_202_ACCEPTED)
def update_user(id: int, user_update: UserUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db_update_user(db, id, user_update)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    return user

@router.delete("/users/{id}", status_code=status.HTTP_200_OK)
def delete_user(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db_delete_user(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"message": "user deleted successfully"}