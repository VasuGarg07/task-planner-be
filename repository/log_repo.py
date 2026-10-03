from db import get_db_conn
from psycopg.types.json import Jsonb

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
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            json_payload = Jsonb(change_record) if isinstance(change_record, (dict, list)) else change_record
            args = (project_id, actor_id, subject_type, subject_id, action_type, json_payload)
            cursor.execute(ADD_LOG_QUERY, args)
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else None

def get_project_logs(project_id):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(SELECT_PROJECT_LOGS_QUERY, (project_id,))
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return []

            columns = ['id', 'timestamp', 'project_id', 'actor_id', 'subject_type', 'subject_id', 'action_type', 'change_record']
            logs = [dict(zip(columns, row)) for row in rows]
            return logs

def get_subject_project(subject_type, subject_id):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            if subject_type == 'SPRINT':
                query = SELECT_SPRINT_PROJECT_QUERY 
            elif subject_type == 'TASK':
                query = SELECT_TASK_PROJECT_QUERY
            cursor.execute(query, (subject_id,))
            row = cursor.fetchone()
            return row[0] if row else None