from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select, text


# --- Table Model (DB) ---
class Vet(SQLModel, table=True):
    __tablename__ = "vets"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    clinic_name: str
    address: str
    latitude: float
    longitude: float
    specialties: Optional[str] = None
    rating: Optional[float] = None
    created_at: Optional[datetime] = Field(default=None)


# --- Request Schemas ---
class VetCreate(SQLModel):
    name: str
    clinic_name: str
    address: str
    latitude: float
    longitude: float
    specialties: Optional[str] = None
    rating: Optional[float] = None

class VetUpdate(SQLModel):
    name: Optional[str] = None
    clinic_name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    specialties: Optional[str] = None
    rating: Optional[float] = None


# --- Response Schema ---
class VetOut(SQLModel):
    id: int
    name: str
    clinic_name: str
    address: str
    latitude: float
    longitude: float
    specialties: Optional[str] = None
    rating: Optional[float] = None
    created_at: Optional[datetime] = None


# --- CRUD Functions ---
def db_create_vet(session: Session, data: VetCreate) -> Vet:
    vet = Vet(**data.model_dump())
    session.add(vet)
    session.commit()
    session.refresh(vet)
    return vet

def db_get_all_vet(session: Session, skip: int = 0, limit: int = 20):
    return session.exec(select(Vet).offset(skip).limit(limit)).all()

def db_get_one_vet(session: Session, id: int):
    return session.get(Vet, id)

def db_update_vet(session: Session, id: int, data: VetUpdate):
    vet = session.get(Vet, id)
    if not vet:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(vet, key, value)
    session.add(vet)
    session.commit()
    session.refresh(vet)
    return vet

def db_delete_vet(session: Session, id: int):
    vet = session.get(Vet, id)
    if not vet:
        return None
    session.delete(vet)
    session.commit()
    return vet

def db_filter_vets(session: Session, specialties: Optional[str] = None, clinic_name: Optional[str] = None):
    query = select(Vet)
    if specialties:
        query = query.where(Vet.specialties.ilike(f"%{specialties}%"))
    if clinic_name:
        query = query.where(Vet.clinic_name.ilike(f"%{clinic_name}%"))
    return session.exec(query).all()

def db_filter_rating_vet(session: Session, rating: float, clinic_name: str):
    return session.exec(
        select(Vet).where(Vet.rating >= rating, Vet.clinic_name == clinic_name)
    ).all()

def db_filter_vets_by_proximity(session: Session, lat: float, lng: float, limit: int = 10):
    result = session.exec(text("""
        SELECT *, 
        ( 6371 * acos( cos( radians(:lat) ) * cos( radians( latitude ) ) 
        * cos( radians( longitude ) - radians(:lng) ) + sin( radians(:lat) ) 
        * sin( radians( latitude ) ) ) ) AS distance 
        FROM vets 
        ORDER BY distance ASC 
        LIMIT :limit
    """), {"lat": lat, "lng": lng, "limit": limit})
    return result.mappings().all()