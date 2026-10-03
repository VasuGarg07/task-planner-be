import os
import json
from psycopg_pool import ConnectionPool

# Ensure the DB already existings. If not, make one via super user "postgres"
# 1. Global reference stays empty on import
db_pool = None

def init_db():
    global db_pool

    if db_pool is not None:
        return db_pool
    
    print("Initializing databse connection pool")

    # Read JSON FILE
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
    else:
        config = {}

    db_kwargs = {
        'host': config.get('DB_HOST', 'localhost'),
        'port': 5432,
        'user': 'postgres',
        'password': config.get('DB_PASSWORD'),
        'dbname': 'task_planner'
    }

    db_pool = ConnectionPool(
        min_size=1,
        max_size=10,
        kwargs=db_kwargs,
        open=False
    )
    db_pool.open()

    return db_pool

def get_db_conn():
    if db_pool is None:
        raise RuntimeError("DB pool not initialized; call init_db() first")
    return db_pool.connection()
