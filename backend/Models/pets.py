from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select


# --- Table Model (DB) ---
class Pet(SQLModel, table=True):
    __tablename__ = "pets"
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id")
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    medical_history: Optional[str] = None
    created_at: Optional[datetime] = Field(default=None)


# --- Request Schemas ---
class PetCreate(SQLModel):
    owner_id: int
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    medical_history: Optional[str] = None

class PetUpdate(SQLModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[int] = None
    medical_history: Optional[str] = None


# --- Response Schema ---
class PetOut(SQLModel):
    id: int
    owner_id: int
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    medical_history: Optional[str] = None
    created_at: Optional[datetime] = None


# --- CRUD Functions ---
def db_create_pets(session: Session, data: PetCreate) -> Pet:
    pet = Pet(**data.model_dump())
    session.add(pet)
    session.commit()
    session.refresh(pet)
    return pet

def db_get_all_pets(session: Session):
    return session.exec(select(Pet)).all()

def db_get_pets_by_owner(session: Session, owner_id: int):
    return session.exec(select(Pet).where(Pet.owner_id == owner_id).order_by(Pet.id.desc())).all()

def db_get_one_pet(session: Session, id: int):
    return session.get(Pet, id)

def db_update_pets(session: Session, id: int, data: PetUpdate):
    pet = session.get(Pet, id)
    if not pet:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(pet, key, value)
    session.add(pet)
    session.commit()
    session.refresh(pet)
    return pet

def db_delete_pet(session: Session, id: int):
    pet = session.get(Pet, id)
    if not pet:
        return None
    session.delete(pet)
    session.commit()
    return pet
