from db import get_pooled_conn, release_pooled_conn

# RAW SQL QUERIES
INSERT_USER_QUERY = """
    INSERT INTO users (username, email, role)
    VALUES (%s, %s, %s)
    RETURNING id;
"""

SELECT_USER_QUERY = """
    SELECT id, username, email, role
    FROM users
    WHERE email = %s;
"""

DELETE_USER_QUERY = """
    DELETE FROM users 
    WHERE id = %s;
"""


def create_user(username, email, role):
    conn = get_pooled_conn()
    cursor = conn.cursor()

    try:
        args = (username, email, role)
        cursor.execute(INSERT_USER_QUERY, args)
        row = cursor.fetchone()
        conn.commit()

        user_id = row[0] if row else None
        return user_id
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_user(email):
    conn = get_pooled_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(SELECT_USER_QUERY, (email,))
        row = cursor.fetchone()
        
        if row is None:
            return None
            
        return row 
    finally:
        cursor.close()
        release_pooled_conn(conn)

def remove_user(user_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(DELETE_USER_QUERY, (user_id,))
        rows_deleted = cursor.rowcount
        
        conn.commit()
        return rows_deleted > 0
    finally:
        cursor.close()
        release_pooled_conn(conn)
