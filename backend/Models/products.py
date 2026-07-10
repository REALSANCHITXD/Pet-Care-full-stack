from database import conn, cursor
from datetime import datetime

def db_create_product(name:str,description:str,price:float,stock:int,category:str,rating:float):
    cursor.execute("""
        INSERT INTO products (name,description,price,stock,category,rating)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING *
    """,(name,description,price,stock,category,rating))
    new_product=cursor.fetchone()
    conn.commit()
    return new_product

def db_get_all_products(skip: int = 0, limit: int = 20):
    cursor.execute("SELECT * FROM products OFFSET %s LIMIT %s", (skip, limit))
    products = cursor.fetchall()
    return products

def db_get_one_product(id:int):
    cursor.execute("SELECT * FROM products WHERE id=%s",(id,))
    product = cursor.fetchone()
    return product

def db_update_product(id:int,update_data:dict):
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(id)
    cursor.execute(f"""
        UPDATE products SET {set_clause} WHERE id = %s RETURNING *
    """,values)
    updated_product = cursor.fetchone()
    conn.commit()
    return updated_product

def db_delete_product(id:int):
    cursor.execute("DELETE FROM products WHERE id = %s RETURNING *",(id,))
    deleted_product = cursor.fetchone()
    conn.commit()
    return deleted_product

def db_filter_products(category:str ,price_up:float,rating:float,price_down:float):
    if category:
        cursor.execute("SELECT * FROM products WHERE category=%s",(category,))
        return cursor.fetchall()
    if price_up:
       cursor.execute("SELECT * FROM products WHERE price<=%s",(price_up,))
       return cursor.fetchall()
    if price_down:
       cursor.execute("SELECT * FROM products WHERE price>=%s",(price_down,))
       return cursor.fetchall()
    if rating:
        cursor.execute("SELECT * FROM products WHERE rating=%s",(rating,))
        return cursor.fetchall()