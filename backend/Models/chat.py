from database import conn, cursor

def db_create_session(user_id: int):
    cursor.execute("""
        INSERT INTO chat_sessions (user_id)
        VALUES (%s) RETURNING *
    """, (user_id,))
    session = cursor.fetchone()
    conn.commit()
    return session

def db_get_session(session_id: int):
    cursor.execute("SELECT * FROM chat_sessions WHERE id = %s", (session_id,))
    return cursor.fetchone()

def db_get_user_sessions(user_id: int):
    cursor.execute("""
        SELECT * FROM chat_sessions WHERE user_id = %s
        ORDER BY started_at DESC
    """, (user_id,))
    return cursor.fetchall()

def db_save_message(session_id: int, sender: str, message: str):
    cursor.execute("""
        INSERT INTO chat_messages (session_id, sender, message)
        VALUES (%s, %s, %s) RETURNING *
    """, (session_id, sender, message))
    msg = cursor.fetchone()
    conn.commit()
    return msg

def db_get_session_messages(session_id: int):
    cursor.execute("""
        SELECT * FROM chat_messages
        WHERE session_id = %s
        ORDER BY sent_at ASC
    """, (session_id,))
    return cursor.fetchall()

def db_count_user_messages_today(user_id: int):
    """Count how many messages the user sent today (for free tier limit)."""
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM chat_messages cm
        JOIN chat_sessions cs ON cm.session_id = cs.id
        WHERE cs.user_id = %s
          AND cm.sender = 'user'
          AND cm.sent_at::date = CURRENT_DATE
    """, (user_id,))
    result = cursor.fetchone()
    return result['count'] if result else 0
