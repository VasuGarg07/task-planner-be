CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(10) DEFAULT 'BA',
    CONSTRAINT check_role CHECK (role IN ('BA', 'DEV', 'QA', 'PM', 'DEV-OPS'))
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    created_at DATE, 
    status VARCHAR(30) DEFAULT 'NOT STARTED',
    CONSTRAINT check_status CHECK (status IN ('NOT STARTED', 'DISCOVERY', 'IN PROGRESS', 'ON HOLD', 'COMPLETED', 'DROPPED'))
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at DATE,
    assignee INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reporter INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'OPEN',
    CONSTRAINT check_status CHECK (status IN ('OPEN', 'IN PROGRESS', 'ON HOLD', 'DONE', 'VOID')),
    CONSTRAINT unique_task_name UNIQUE (project_id, name)
);

CREATE TABLE IF NOT EXISTS sprints (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    max_capacity INTEGER NOT NULL,
    status VARCHAR (20) DEFAULT 'PLANNING',
    CONSTRAINT check_status CHECK (status IN ('PLANNING', 'ACTIVE', 'COMPLETED'))
);

ALTER TABLE tasks ADD COLUMN IF NOT EXISTS story_points INTEGER DEFAULT 0;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS sprint_id INTEGER REFERENCES sprints(id) ON DELETE SET NULL;