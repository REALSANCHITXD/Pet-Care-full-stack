from fastapi import HTTPException
from pydantic import EmailStr
from database import conn, cursor
from utils import hash_password

def db_create_user(email, password, full_name, role, subscription_tier, default_address=None):
    hashed = hash_password(password)
    cursor.execute("""INSERT INTO users (email,hashed_password,full_name,role,subscription_tier,default_address) VALUES (%s,%s,%s,%s,%s,%s) RETURNING * """,(email,hashed,full_name,role,subscription_tier,default_address))
    new_post = cursor.fetchone()
    conn.commit()
    return new_post

def db_get_users():
    cursor.execute("""SELECT * FROM users""")
    posts = cursor.fetchall()
    return posts

def db_get_one_user(id):
    cursor.execute("SELECT * FROM users WHERE id = %s",(id,))
    posts_one = cursor.fetchone()
    return posts_one

def db_update_user(id: int,user_update:dict):
    # Hash password if being updated
    if 'password' in user_update:
        user_update['hashed_password'] = hash_password(user_update.pop('password'))

    set_clause = ", ".join([f"{key} = %s" for key in user_update.keys()])
    values = list(user_update.values())
    values.append(id)
    
    cursor.execute(f"""UPDATE users SET {set_clause} WHERE id = %s RETURNING *""", values)
    updated_user =cursor.fetchone()
    conn.commit()
    return updated_user
    
def db_delete_user(id):
    cursor.execute("""DELETE FROM users WHERE id = %s RETURNING *""",(id,))
    delete_user = cursor.fetchone()
    conn.commit()
    return delete_user

def db_get_user_by_email(email):
    cursor.execute("SELECT * FROM users WHERE email = %s",(email,))
    user = cursor.fetchone()
    return user
