import os
import json
import psycopg2
from psycopg2 import pool

# Ensure the DB already existings. If not, make one via super user "postgres"
DB_NAME = 'task_planner'
db_pool = None

# Read JSON FILE
if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)
else:
    config = {}

def initialize_db_pool():
    global db_pool
    try:
        print("Initializing databse connection pool")
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=config.get('DB_HOST', 'localhost'),
            port=5432,
            user='postgres',
            password=config.get('DB_PASSWORD'),
            dbname=DB_NAME
        )
    except Exception as e:
        print(f"Failed to create db pool: {e}")

initialize_db_pool()

def get_pooled_conn():
    global db_pool
    return db_pool.getconn()

def release_pooled_conn(conn):
    global db_pool
    db_pool.putconn(conn)

if __name__ == '__main__':
    try:
        # Connect DB and get cursor
        print("Connecting to db...")
        conn = get_pooled_conn()
        cursor = conn.cursor()

        # Read schema.sql
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()

        # Execute raw SQL text
        print("Creating tables in db if not available")
        cursor.execute(schema_sql)
        conn.commit() # Permanently writes changes to disk
        print(f"All tables created in db: {DB_NAME}")

        # Clean up and close
        cursor.close()
        release_pooled_conn(conn)

    except Exception as e:
        print(f"\n DB initialization failed")
        print(f"Error Details: {e}")

