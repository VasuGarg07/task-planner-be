from flask import Flask, jsonify

from db import init_db, get_db_conn
from routes.users import users_bp
from routes.projects import projects_bp
from routes.tasks import tasks_bp
from routes.sprints import sprints_bp

app = Flask(__name__)

init_db()

@app.route('/health')
def health_check():
    try:
        # Globally accessible, thread-safe, and cleanly isolated
        with get_db_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                output = cursor.fetchone()
                print(f"output: {output}")

        return jsonify({"status": "healthy", "database":"connected"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

app.register_blueprint(users_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(sprints_bp)

if __name__ == '__main__': 
    app.run(debug=True, port=5000) 