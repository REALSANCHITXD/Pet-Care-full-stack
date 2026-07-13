from typing import Optional
from sqlmodel import SQLModel, Field, Session, select
from pydantic import EmailStr
from fastapi import HTTPException
from utils import hash_password
from enum import Enum


# --- Enums ---
class UserRole(str, Enum):
    owner = "owner"
    veterinary = "veterinary"
    customer = "customer"

class SubscriptionTier(str, Enum):
    free = "free"
    premium = "premium"


# --- Table Model (DB) ---
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: str = Field(default=UserRole.customer)
    subscription_tier: str = Field(default=SubscriptionTier.free)
    default_address: Optional[str] = None


# --- Request Schemas ---
class UserCreate(SQLModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[UserRole] = UserRole.customer
    subscription_tier: Optional[SubscriptionTier] = SubscriptionTier.free
    default_address: Optional[str] = None

class UserUpdate(SQLModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    subscription_tier: Optional[SubscriptionTier] = None
    default_address: Optional[str] = None

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str


# --- Response Schema ---
class UserOut(SQLModel):
    id: int
    email: str
    full_name: str
    role: str
    subscription_tier: str
    default_address: Optional[str] = None


# --- CRUD Functions ---
def db_create_user(session: Session, data: UserCreate) -> User:
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        subscription_tier=data.subscription_tier,
        default_address=data.default_address,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def db_get_users(session: Session):
    return session.exec(select(User)).all()

def db_get_one_user(session: Session, id: int):
    return session.get(User, id)

def db_get_user_by_email(session: Session, email: str):
    return session.exec(select(User).where(User.email == email)).first()

def db_update_user(session: Session, id: int, data: UserUpdate):
    user = session.get(User, id)
    if not user:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    for key, value in update_data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def db_delete_user(session: Session, id: int):
    user = session.get(User, id)
    if not user:
        return None
    session.delete(user)
    session.commit()
    return user
