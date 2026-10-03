from db import get_db_conn

# RAW SQL QUERY CONSTANTS
INSERT_TASK_QUERY = """
    INSERT INTO tasks (project_id, name, description, reporter, assignee, created_at, status)
    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, 'OPEN')
    RETURNING id;
"""

SELECT_TASK_BY_ID_QUERY = """
    SELECT id, project_id, name, description, reporter, assignee, created_at, status, sprint_id, story_points
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

TASKS_BASE_QUERY = """
    SELECT id, project_id, name, description, reporter, assignee, created_at, status, sprint_id, story_points
    FROM tasks
    WHERE project_id = %s
"""

def create_task(project_id, name, description, reporter_id, assignee_id=None):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            args = (project_id, name, description, reporter_id, assignee_id)
            cursor.execute(INSERT_TASK_QUERY, args)
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else None

def get_task(task_id):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(SELECT_TASK_BY_ID_QUERY, (task_id,))
            row = cursor.fetchone()
            return row if row else None

def delete_task_from_db(task_id):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(DELETE_TASK_QUERY, (task_id,))
            rows_deleted = cursor.rowcount
            conn.commit()
            return rows_deleted > 0

def check_user_exists_globally(user_id):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(CHECK_USER_EXISTS_QUERY, (user_id,))
            return cursor.fetchone() is not None

def update_task_assignee(task_id, assignee_id):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(UPDATE_TASK_ASSIGNEE_QUERY, (assignee_id, task_id))
            rows_updated = cursor.rowcount
            conn.commit()
            return rows_updated > 0

def update_task_status(task_id, new_status):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(UPDATE_TASK_STATUS_QUERY, (new_status, task_id))
            rows_updated = cursor.rowcount
            conn.commit()
            return rows_updated > 0

def update_task_story_points(task_id, story_points):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(UPDATE_TASK_STORY_POINTS_QUERY, (story_points, task_id))
            rows_updated = cursor.rowcount
            conn.commit()
            return rows_updated > 0

def fetch_task_list(project_id, status=None, page_num=1, page_size=10):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            project_id = int(project_id)
            limit = int(page_size)
            offset = (int(page_num) - 1) * limit
            query = TASKS_BASE_QUERY

            if status is not None:
                query += """ AND status = %s """

            query += """
            LIMIT %s OFFSET %s
            """

            args = (project_id, limit, offset) if status is None else (project_id, status, limit, offset)
            cursor.execute(query, args)
            rows = cursor.fetchall()

            if not rows:
                return []

            columns = ['id', 'project_id', 'name', 'description', 'reporter', 'assignee', 'created_at', 'status', 'sprint_id', 'story_points']
            data = [dict(zip(columns, row)) for row in rows]
            return data