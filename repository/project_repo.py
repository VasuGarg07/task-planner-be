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

SPRINT_CAPACITY_QUERY = """
    SELECT s.id, s.name, s.start_date, s.end_date, s.max_capacity, s.status,
        COALESCE(SUM(t.story_points), 0) AS current_capacity
    FROM sprints s
        LEFT JOIN tasks t
        ON s.id = t.sprint_id
    WHERE s.project_id = %s 
    GROUP BY s.id, s.name, s.start_date, s.end_date, s.max_capacity, s.status;
"""


def create_project(name, description):
    conn = get_pooled_conn()
    cursor = conn.cursor()

    try:
        args = name, description
        cursor.execute(INSERT_PROJECT_QUERY, args)
        row = cursor.fetchone()
        conn.commit()
        return row[0] if row else None
    finally:
        cursor.close()
        release_pooled_conn(conn)

def get_project(project_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(SELECT_PROJECT_QUERY, (project_id,))
        row = cursor.fetchone()
        return row if row else None
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

def get_sprint_capacity_report(project_id):
    conn = get_pooled_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(SPRINT_CAPACITY_QUERY, (project_id,))
        rows = cursor.fetchall()

        if rows is None:
            return []

        print(rows)
        columns = ['sprint_id', 'name', 'start_date', 'end_date', 'max_capacity', 'status', 'current_capacity']
        sprints = [dict(zip(columns, row)) for row in rows]

        return sprints
    finally:
        cursor.close()
        release_pooled_conn(conn)