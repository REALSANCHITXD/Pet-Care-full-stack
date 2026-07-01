from database import conn, cursor


def db_create_pets(owner_id:int , name: str, species:str ,breed=None , age=None, medical_history=None):
    cursor.execute("""INSERT INTO pets (owner_id,name ,species ,breed ,age ,medical_history) VALUES(%s,%s,%s,%s,%s,%s) RETURNING *""",(owner_id,name,species,breed,age,medical_history))
    new_pet= cursor.fetchone()
    conn.commit()
    return new_pet

def db_get_all_pets():
    cursor.execute("SELECT * FROM pets")
    pets = cursor.fetchall()
    return pets

def db_get_pets_by_owner(owner_id: int):
    cursor.execute("SELECT * FROM pets WHERE owner_id = %s ORDER BY id DESC", (owner_id,))
    pets = cursor.fetchall()
    return pets

def db_get_one_pet(id : int):
    cursor.execute("SELECT * FROM pets WHERE id = %s",(str(id),))
    pet_one = cursor.fetchone()
    return pet_one

def db_update_pets(id:int , pet_update:dict):
    set_clause = ",".join(f"{key} =%s" for key in pet_update.keys())
    values = list(pet_update.values())
    values.append(id)

    cursor.execute(f"UPDATE pets SET {set_clause} WHERE id=%s RETURNING *",values)
    updated_pet = cursor.fetchone()
    conn.commit()
    return updated_pet

def db_delete_pet(id:int):
    cursor.execute("DELETE FROM pets WHERE id=%s RETURNING *",(str(id),))
    deleted_pet = cursor.fetchone()
    conn.commit()
    return deleted_pet

