from database import conn, cursor
from datetime import datetime
from typing import Optional

def db_booking_create(user_id:int , vet_id:int,appointment_time:datetime , reason:Optional[str]=None):
    # Check for collision
    cursor.execute("SELECT * FROM bookings WHERE vet_id=%s AND appointment_time=%s", (vet_id, appointment_time))
    if cursor.fetchone():
        return None # Collision detected
        
    cursor.execute("INSERT INTO bookings (user_id,vet_id,appointment_time ,reason) VALUES(%s,%s,%s,%s) RETURNING *",(user_id,vet_id,appointment_time,reason))
    new_book=cursor.fetchone()
    conn.commit()
    return new_book

def db_booking_get_by_user(user_id: int):
    cursor.execute("SELECT * FROM bookings WHERE user_id=%s", (user_id,))
    return cursor.fetchall()

def db_booking_get_all():
    cursor.execute("SELECT * FROM bookings")
    all_bookings=cursor.fetchall()
    return all_bookings

def db_booking_get_one(id:int):
    cursor.execute("SELECT * FROM bookings WHERE id=%s",(str(id),))
    one_booking=cursor.fetchone()
    return one_booking

def db_booking_update(id:int, update_dict: dict):
    set_clause = ",".join(f"{key}=%s" for key in update_dict.keys())
    values = list(update_dict.values())
    values.append(id)
    cursor.execute(f"UPDATE bookings SET {set_clause} WHERE id=%s RETURNING *", values)
    updated_booking=cursor.fetchone()
    conn.commit()
    return updated_booking

def db_booking_delete(id:int):
    cursor.execute("DELETE FROM bookings WHERE id=%s RETURNING *", (str(id),))
    deleted_book = cursor.fetchone()
    conn.commit()
    return deleted_book