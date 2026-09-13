from db import get_pooled_conn, release_pooled_conn

# RAW SQL QUERIES
INSERT_PROJECT_QUERY = """
    INSERT INTO projects (name, description, created_at, status)
    VALUES (%s, %s, CURRENT_DATE, 'NOT STARTED')
    RETURNING id;
"""
SELECT_PROJECT_QUERY = """
    SELECT * FROM projects
    WHERE id = %s
"""
DELETE_PROJECT_QUERY = """
    DELETE FROM projects
    WHERE id = %s
"""
UPDATE_PROJECT_STATUS_QUERY = """
    UPDATE projects 
    SET status = %s 
    WHERE id = %s;
"""


def create_project(name, description):
    conn = get_pooled_conn()
    cursor = conn.cursor()

    try:
        args = name, description
        cursor.execute(INSERT_PROJECT_QUERY, args)
        row = cursor.fetchone()

        if row is None:
                return None
                
        print(f"user details: {row}")
        return row 
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_project(project_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(SELECT_PROJECT_QUERY, (project_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
            
        print(f"project found: {row}")
        return row
    finally:
        cursor.close()
        release_pooled_conn(conn)

def remove_project(project_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(DELETE_PROJECT_QUERY, (project_id,))
        rows_deleted = cursor.rowcount

        conn.commit()
        return rows_deleted > 0

    finally:
        cursor.close()
        release_pooled_conn(conn)

def update_project_status_in_db(project_id, new_status):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(UPDATE_PROJECT_STATUS_QUERY, (new_status, project_id))
        rows_updated = cursor.rowcount
        conn.commit()
        return rows_updated > 0
    finally:
        cursor.close()
        release_pooled_conn(conn)
