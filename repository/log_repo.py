from db import get_pooled_conn, release_pooled_conn
from psycopg2.extras import Json

# RAW SQL QUERIES
ADD_LOG_QUERY = """
    INSERT INTO logs (timestamp, project_id, actor_id, subject_type, subject_id, action_type, change_record)
    VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s)
    RETURNING id;
"""

SELECT_PROJECT_LOGS_QUERY = """
    SELECT id, timestamp, project_id, actor_id, subject_type, subject_id, action_type, change_record
    FROM logs
    WHERE project_id = %s
    ORDER BY timestamp DESC;
"""

SELECT_SPRINT_PROJECT_QUERY = """
    SELECT project_id
    FROM sprints
    WHERE id = %s;
"""

SELECT_TASK_PROJECT_QUERY = """
    SELECT project_id
    FROM tasks
    WHERE id = %s;
"""


def create_log(project_id, actor_id, subject_type, subject_id, action_type, change_record):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        json_payload = Json(change_record) if isinstance(change_record, (dict, list)) else change_record
        args = (project_id, actor_id, subject_type, subject_id, action_type, json_payload)
        cursor.execute(ADD_LOG_QUERY, args)
        row = cursor.fetchone()
        conn.commit()
        return row[0] if row else None
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_project_logs(project_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(SELECT_PROJECT_LOGS_QUERY, (project_id,))
        rows = cursor.fetchall()\

        if rows is None:
            return []

        columns = ['id', 'timestamp', 'project_id', 'actor_id', 'subject_type', 'subject_id', 'action_type', 'change_record']
        logs = [dict(zip(columns, row)) for row in rows]
        return logs
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_subject_project(subject_type, subject_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        if subject_type == 'SPRINT':
            query = SELECT_SPRINT_PROJECT_QUERY 
        elif subject_type == 'TASK':
            query = SELECT_TASK_PROJECT_QUERY
        cursor.execute(query, (subject_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        release_pooled_conn(conn)