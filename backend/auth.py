from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import Session
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

from database import get_db
from Models.Users import Token, db_get_user_by_email, db_get_one_user
from utils import create_access_token, verify_password

env_path = os.path.join(os.path.dirname(__file__), "secret.env")
load_dotenv(dotenv_path=env_path)

router = APIRouter(tags=["AUTHENTICATION"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db_get_user_by_email(db, login.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    token = create_access_token(data={"user_id": user.id, "role": user.role})
    return Token(access_token=token, token_type="bearer")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db_get_one_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
