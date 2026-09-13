from db import get_pooled_conn, release_pooled_conn

# RAW SQL QUERY CONSTANTS
INSERT_TASK_QUERY = """
    INSERT INTO tasks (project_id, name, description, reporter, assignee, created_at, status)
    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, 'OPEN')
    RETURNING id;
"""

SELECT_TASK_BY_ID_QUERY = """
    SELECT id, project_id, name, description, reporter, assignee, created_at, status 
    FROM tasks 
    WHERE id = %s;
"""

DELETE_TASK_QUERY = """
    DELETE FROM tasks 
    WHERE id = %s;
"""

def create_task(project_id, name, description, reporter_id, assignee_id=None):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        args = (project_id, name, description, reporter_id, assignee_id)
        cursor.execute(INSERT_TASK_QUERY, args)
        task_id = cursor.fetchone()[0]
        
        conn.commit()
        print(f"output task_id created: {task_id}")
        return task_id
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_task(task_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(SELECT_TASK_BY_ID_QUERY, (task_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
            
        print(f"task found: {row}")
        return row
    finally:
        cursor.close()
        release_pooled_conn(conn)

def delete_task_from_db(task_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(DELETE_TASK_QUERY, (task_id,))
        rows_deleted = cursor.rowcount
        
        conn.commit()
        return rows_deleted > 0
    finally:
        cursor.close()
        release_pooled_conn(conn)
