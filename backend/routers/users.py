from fastapi import APIRouter, status, HTTPException, Depends
from typing import Optional, List
from fastapi import Body

from auth import get_current_user

# Import database functions
from Models.Users import db_create_user, db_get_users, db_get_one_user,db_update_user,db_delete_user

# Import schemas
from schemas.users import UserRole, SubscriptionTier, users_create, users_out, users_update

router = APIRouter()

@router.post('/users', response_model=users_out, status_code=status.HTTP_201_CREATED)
def create_user(user_data: users_create):
    new_post = db_create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role,
        subscription_tier=user_data.subscription_tier
    )
    if not new_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"user with email {user_data.email} could not be created")
    return new_post

@router.get("/users", response_model=List[users_out],status_code=status.HTTP_200_OK)
def get_users(current_user: str = Depends(get_current_user)):
    posts = db_get_users()
    return posts

@router.get("/users/me", response_model=users_out, status_code=status.HTTP_200_OK)
def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the currently authenticated user's profile."""
    return current_user

@router.get("/users/{id}", response_model=users_out, status_code=status.HTTP_200_OK)
def get_one_user(id:int, current_user: str = Depends(get_current_user)):
    posts_one = db_get_one_user(id)
    if not posts_one:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with {id} is not found") 
    
    return posts_one

@router.patch("/users/{id}",response_model = users_out,status_code=status.HTTP_202_ACCEPTED)
def update_user(id:int ,user_update:users_update, current_user: str = Depends(get_current_user)):
    user= db_update_user(id,user_update.dict(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with this {id} was not there")
    return user

@router.delete("/users/{id}",status_code=status.HTTP_200_OK)
def delete_user(id:int, current_user: str = Depends(get_current_user)):
    user = db_delete_user(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"message":"user deleted successfully"}