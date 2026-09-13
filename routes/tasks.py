from flask import Blueprint, request, jsonify, g
from middlewares.auth import requires_auth
from repository.task_repo import create_task, get_task, delete_task_from_db

tasks_bp = Blueprint('tasks_bp', __name__)

@tasks_bp.route("/tasks", methods=['POST'])
@requires_auth
def post_task():
    data = request.get_json() or {}
    project_id = data.get('project_id')
    name = data.get('name')
    description = data.get('description', '')
    assignee_id = data.get('assignee_id')

    if not project_id or not name:
        return jsonify({"error": "Project ID and Task Name are required"}), 400

    try:
        new_task_id = create_task(project_id, name, description, g.current_user_id, assignee_id)
        return jsonify({"id": new_task_id, "message": "Task card created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/tasks/<int:task_id>", methods=['GET'])
@requires_auth
def get_task_profile(task_id):
    try:
        task_row = get_task(task_id)
        
        if task_row is None:
            return jsonify({"error": "Task card not found"}), 404
            
        return jsonify({
            "id": task_row[0],
            "project_id": task_row[1],
            "name": task_row[2],
            "description": task_row[3],
            "reporter_id": task_row[4],
            "assignee_id": task_row[5],
            "created_at": str(task_row[6]),
            "status": task_row[7]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/tasks/<int:task_id>", methods=['DELETE'])
@requires_auth
def delete_task(task_id):
    try:
        was_deleted = delete_task_from_db(task_id)
        
        if not was_deleted:
            return jsonify({"error": "Task card not found"}), 404
            
        return jsonify({"message": f"Task {task_id} deleted cleanly"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
