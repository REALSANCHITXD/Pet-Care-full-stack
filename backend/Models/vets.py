from database import conn, cursor
from typing import Optional

def db_create_vet(name :str,clinic_name:str,address:str,latitude:float,longitude:float,specialties:Optional[str]=None,rating:Optional[float]=None):
    cursor.execute("INSERT INTO vets (name,clinic_name,address,latitude,longitude,specialties,rating) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *",(
        name,clinic_name,address,latitude,longitude,specialties,rating
    ))
    new_vet=cursor.fetchone()
    conn.commit()
    return new_vet

def db_get_all_vet(skip: int = 0, limit: int = 20):
    cursor.execute("SELECT * FROM vets OFFSET %s LIMIT %s", (skip, limit))
    all_vet = cursor.fetchall()
    return all_vet

def db_get_one_vet(id:int):
    cursor.execute("SELECT * FROM vets WHERE id = %s", (str(id),))
    one_vet = cursor.fetchone()
    return one_vet


def db_update_vet(id:int ,vet_update:dict):
    set_clause = ",".join(f"{key}=%s"for key in vet_update.keys())
    values= list(vet_update.values())
    values.append(id)
    cursor.execute(f"UPDATE vets SET {set_clause} WHERE id = %s RETURNING *",values)
    updated_vet = cursor.fetchone()
    conn.commit()
    return updated_vet

def db_delete_vet(id:int):
    cursor.execute("DELETE FROM vets WHERE id = %s RETURNING *", (str(id),))
    deleted_vet = cursor.fetchone()
    conn.commit()
    return deleted_vet

def db_filter_vets(specialties:str,clinic_name:str):
    cursor.execute("SELECT * FROM vets WHERE specialties = %s AND clinic_name = %s",(specialties,clinic_name))
    filter_vets = cursor.fetchall()
    return filter_vets
    
def db_filter_rating_vet(rating:str,clinic_name:str):
    cursor.execute("SELECT * FROM vets WHERE rating >= %s AND clinic_name = %s",(rating,clinic_name))
    filter_rating_vet = cursor.fetchall()
    return filter_rating_vet

def db_filter_vets_by_proximity(lat: float, lng: float, limit: int = 10):
    cursor.execute("""
        SELECT *, 
        ( 6371 * acos( cos( radians(%s) ) * cos( radians( latitude ) ) 
        * cos( radians( longitude ) - radians(%s) ) + sin( radians(%s) ) 
        * sin( radians( latitude ) ) ) ) AS distance 
        FROM vets 
        ORDER BY distance ASC 
        LIMIT %s
    """, (lat, lng, lat, limit))
    return cursor.fetchall()