from Models.Users import db_get_user_by_email, db_get_one_user
from fastapi import APIRouter,Depends,status,HTTPException,Response
from schemas.users import User_Login,Token
from utils import create_access_token,verify_password
from fastapi.security.oauth2 import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from jose import jwt,JWTError
from schemas import *

env_path = os.path.join(os.path.dirname(__file__), "secret.env")
load_dotenv(dotenv_path=env_path)

router = APIRouter(tags=["AUTHENTICATION"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login",response_model=Token, status_code=status.HTTP_200_OK)
def login(login : OAuth2PasswordRequestForm = Depends()):
    user = db_get_user_by_email(login.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if not verify_password(login.password,user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid password")
    token = create_access_token(data={"user_id":user["id"],"role": user["role"]})
    return Token(
        access_token=token,
        token_type="bearer"
    )

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload =jwt.decode(token,os.getenv("SECRET_KEY"),os.getenv("ALGORITHM"))
        id:str = payload.get('user_id')
        role:str = payload.get('role')
        if id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token")
    user = db_get_one_user(id)
    if not user :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
    return user
