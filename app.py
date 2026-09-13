from flask import Flask, jsonify, request

from db import get_pooled_conn, release_pooled_conn
from routes.users import users_bp
from routes.projects import projects_bp
from routes.tasks import tasks_bp
from routes.sprints import sprints_bp

app = Flask(__name__)

@app.route('/health')
def health_check():
    try:
        conn = get_pooled_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        output = cursor.fetchone()
        print(f"output: {output}")

        cursor.close()
        release_pooled_conn(conn)
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