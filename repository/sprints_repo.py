from db import get_pooled_conn, release_pooled_conn

# RAW SQL QUERIES
INSERT_SPRINT_QUERY = """
    INSERT INTO sprints (project_id, name, start_date, end_date, max_capacity, status)
    VALUES (%s, %s, %s, %s, %s, 'PLANNING')
    RETURNING id;
"""

SELECT_SPRINT_QUERY = """
    SELECT id, project_id, name, start_date, end_date, max_capacity, status 
    FROM sprints
    WHERE id = %s;
"""

UPDATE_SPRINT_STATUS = """
    UPDATE sprints
    SET status = %s
    WHERE id = %s
    RETURNING status;
"""

SUM_SPRINT_STORY_POINTS = """
    SELECT COALESCE(SUM(story_points), 0) 
    FROM tasks 
    WHERE sprint_id = %s;
"""

UPDATE_TASK_SPRINT_MAPPING = """
    UPDATE tasks 
    SET sprint_id = %s 
    WHERE id = %s;
"""

BATCH_CARRY_OVER_QUERY = """
    UPDATE tasks
    SET sprint_id = NULL
    WHERE sprint_id = %s AND status NOT IN ('DONE', 'VOID');
"""


def create_sprint(project_id, name, start_date, end_date, max_capacity):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        args = (project_id, name, start_date, end_date, max_capacity)
        cursor.execute(INSERT_SPRINT_QUERY, args)
        row = cursor.fetchone()
        conn.commit()
        return row[0] if row else None
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_sprint(sprint_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(SELECT_SPRINT_QUERY, (sprint_id,))
        row = cursor.fetchone()
        return row if row else None
    finally:
        cursor.close()
        release_pooled_conn(conn)

def update_sprint_status_in_db(sprint_id, new_status):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(UPDATE_SPRINT_STATUS, (new_status, sprint_id))
        row = cursor.fetchone()

        if new_status == 'COMPLETED':
            cursor.execute(BATCH_CARRY_OVER_QUERY, (sprint_id,))
            print(f"Sprint {sprint_id} closed: Unfinished tasks evicted to backlog.")

        conn.commit()
        return row[0] if row else None
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_sprint_current_weight(sprint_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(SUM_SPRINT_STORY_POINTS, (sprint_id,))
        row = cursor.fetchone()
        return row[0] if row else 0
    finally:
        cursor.close()
        release_pooled_conn(conn)

def assign_task_to_sprint(task_id, sprint_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(UPDATE_TASK_SPRINT_MAPPING, (sprint_id, task_id))
        conn.commit()
    finally:
        cursor.close()
        release_pooled_conn(conn)
