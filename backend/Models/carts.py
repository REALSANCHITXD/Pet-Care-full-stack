from database import conn, cursor

def db_get_or_create_cart(user_id: int):
    cursor.execute("SELECT * FROM carts WHERE user_id = %s", (user_id,))
    cart = cursor.fetchone()
    if not cart:
        cursor.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING *", (user_id,))
        cart = cursor.fetchone()
        conn.commit()
    return cart

def db_add_cart_item(cart_id: int, product_id: int, quantity: int):
    cursor.execute("SELECT * FROM cart_items WHERE cart_id = %s AND product_id = %s", (cart_id, product_id))
    existing_item = cursor.fetchone()
    
    if existing_item:
        cursor.execute("""
            UPDATE cart_items SET quantity = quantity + %s 
            WHERE cart_id = %s AND product_id = %s RETURNING *
        """, (quantity, cart_id, product_id))
        item = cursor.fetchone()
    else:
        cursor.execute("""
            INSERT INTO cart_items (cart_id, product_id, quantity)
            VALUES (%s, %s, %s) RETURNING *
        """, (cart_id, product_id, quantity))
        item = cursor.fetchone()
        
    conn.commit()
    return item

def db_get_cart_items(cart_id: int):
    cursor.execute("""
        SELECT ci.id, ci.cart_id, ci.product_id, ci.quantity, 
               p.name as product_name, p.price as price, 
               (ci.quantity * p.price) as subtotal
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = %s
    """, (cart_id,))
    return cursor.fetchall()

def db_remove_cart_item(item_id: int):
    cursor.execute("DELETE FROM cart_items WHERE id = %s RETURNING *", (item_id,))
    deleted = cursor.fetchone()
    conn.commit()
    return deleted

def db_delete_cart(cart_id: int):
    cursor.execute("DELETE FROM carts WHERE id = %s RETURNING *", (cart_id,))
    deleted = cursor.fetchone()
    conn.commit()
    return deleted
