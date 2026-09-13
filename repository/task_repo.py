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

CHECK_USER_EXISTS_QUERY = """
    SELECT 1 FROM users WHERE id = %s;
"""

UPDATE_TASK_ASSIGNEE_QUERY = """
    UPDATE tasks 
    SET assignee = %s 
    WHERE id = %s;
"""

UPDATE_TASK_STATUS_QUERY = """
    UPDATE tasks
    SET status = %s
    WHERE id = %s;
"""

UPDATE_TASK_STORY_POINTS_QUERY = """
    UPDATE tasks
    SET story_points = %s
    WHERE id = %s;
"""

def create_task(project_id, name, description, reporter_id, assignee_id=None):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        args = (project_id, name, description, reporter_id, assignee_id)
        cursor.execute(INSERT_TASK_QUERY, args)
        row = cursor.fetchone()
        conn.commit()
        return row[0] if row else None
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_task(task_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(SELECT_TASK_BY_ID_QUERY, (task_id,))
        row = cursor.fetchone()
        return row if row else None
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

def check_user_exists_globally(user_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(CHECK_USER_EXISTS_QUERY, (user_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        release_pooled_conn(conn)

def update_task_assignee(task_id, assignee_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(UPDATE_TASK_ASSIGNEE_QUERY, (assignee_id, task_id))
        conn.commit()
    finally:
        cursor.close()
        release_pooled_conn(conn)

def update_task_status(task_id, new_status):
    conn = get_pooled_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(UPDATE_TASK_STATUS_QUERY, (new_status, task_id))
        rows_updated = cursor.rowcount
        conn.commit()
        return rows_updated > 0
    finally:
        cursor.close()
        release_pooled_conn(conn)

def update_task_story_points(task_id, story_points):
    conn = get_pooled_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(UPDATE_TASK_STORY_POINTS_QUERY, (story_points, task_id))
        rows_updated = cursor.rowcount
        conn.commit()
        return rows_updated > 0
    finally:
        cursor.close()
        release_pooled_conn(conn)