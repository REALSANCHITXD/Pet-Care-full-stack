from database import conn,cursor

def db_create_order(user_id: int, shipping_address: str):
    try:
        cursor.execute("SELECT * FROM carts WHERE user_id = %s", (user_id,))
        cart = cursor.fetchone()
        if not cart:
            return None
        
        cursor.execute("""
            SELECT ci.product_id, ci.quantity, p.price 
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = %s
        """, (cart['id'],))
        items = cursor.fetchall()
        
        if not items:
            return None
            
        total_amount = sum(item['quantity'] * item['price'] for item in items)
        
        # Create order
        cursor.execute("""
            INSERT INTO orders (user_id, shipping_address, total_amount, status)
            VALUES (%s, %s, %s, 'pending')
            RETURNING *
        """, (user_id, shipping_address, total_amount))
        new_order = cursor.fetchone()
        
        # Move to order_items & decrement stock
        for item in items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
                VALUES (%s, %s, %s, %s)
            """, (new_order['id'], item['product_id'], item['quantity'], item['price']))
            cursor.execute("""
                UPDATE products SET stock = GREATEST(stock - %s, 0) WHERE id = %s
            """, (item['quantity'], item['product_id']))

        # Delete cart (cascade will delete cart_items)
        cursor.execute("DELETE FROM carts WHERE id = %s", (cart['id'],))
        
        conn.commit()
        
        # Attach items for API response
        new_order['items'] = db_get_order_items(new_order['id'])
        return new_order
    except Exception as e:
        conn.rollback()
        print("Error during checkout transaction:", e)
        return None

def db_get_order_items(order_id: int):
    cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
    return cursor.fetchall()

def db_get_orders():
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    for o in orders:
        o['items'] = db_get_order_items(o['id'])
    return orders

def db_get_orders_by_user(user_id: int):
    cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY id DESC", (user_id,))
    orders = cursor.fetchall()
    for o in orders:
        o['items'] = db_get_order_items(o['id'])
    return orders

def db_get_one_order(id):
    cursor.execute("SELECT * FROM orders WHERE id = %s", (id,))
    order = cursor.fetchone()
    if order:
        order['items'] = db_get_order_items(order['id'])
    return order

def db_update_order(id, update_data):
    if not update_data:
        return db_get_one_order(id)
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(id) 
    
    cursor.execute(f"""
        UPDATE orders SET {set_clause} WHERE id = %s RETURNING *
    """, values)
    
    updated_order = cursor.fetchone()
    conn.commit()
    if updated_order:
        updated_order['items'] = db_get_order_items(id)
    return updated_order

def db_delete_order(id):
    cursor.execute("DELETE FROM orders WHERE id = %s RETURNING *", (id,))
    deleted_order = cursor.fetchone()
    conn.commit()
    return deleted_order

def db_mark_order_paid(id):
    cursor.execute("UPDATE orders SET status = 'paid' WHERE id = %s RETURNING *", (id,))
    updated_order = cursor.fetchone()
    conn.commit()
    if updated_order:
        updated_order['items'] = db_get_order_items(id)
    return updated_order
