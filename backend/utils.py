from passlib.context import CryptContext
from confg import JWT_SECRET,JWT_EXPIRE_MINUTES,JWT_ALGORITHM
from jose import jwt ,JWTError
from datetime import datetime,timedelta,timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,JWT_SECRET,algorithm=JWT_ALGORITHM)
    return encoded_jwt
   