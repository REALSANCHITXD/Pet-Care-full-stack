from pydantic import EmailStr
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class UserRole(str ,Enum):
    owner = "owner"
    vetenary = "vetenary"
    customer = "customer"

class SubscriptionTier(str,Enum):
    free = "free"
    premium = "premium"

class users_create(BaseModel):
    email: EmailStr
    password: str 
    full_name: str
    role: Optional[UserRole] = UserRole.customer
    subscription_tier: Optional[SubscriptionTier] = SubscriptionTier.free
    default_address: Optional[str] = None

class users_out(BaseModel):
    email:str
    id :int
    full_name:str
    role: UserRole
    subscription_tier : SubscriptionTier
    default_address: Optional[str] = None

class users_update(BaseModel):
    email : Optional[str] =None
    password:Optional[str] = None
    full_name:Optional[str] = None
    role: Optional[UserRole] =None
    subscription_tier: Optional[SubscriptionTier] = None
    default_address: Optional[str] = None

class User_Login(BaseModel):
    email:EmailStr
    password:str
    
class Token(BaseModel):
    access_token: str
    token_type: str