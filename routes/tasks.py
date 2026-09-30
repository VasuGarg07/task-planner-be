from flask import Blueprint, request, jsonify, g
from middlewares.auth import requires_auth
from repository.task_repo import create_task, fetch_task_list, get_task, delete_task_from_db, check_user_exists_globally, update_task_assignee, update_task_status, update_task_story_points
from middlewares.logger import log_action

tasks_bp = Blueprint('tasks_bp', __name__)

@tasks_bp.route("/tasks", methods=['POST'])
@requires_auth
@log_action('TASK')
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
        return jsonify({"task_id": new_task_id, "message": "Task card created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/tasks/<int:task_id>", methods=['GET'])
@requires_auth
def get_task_profile(task_id):
    try:
        task_row = get_task(task_id)
        
        if task_row is None:
            return jsonify({"error": "Task not found"}), 404
            
        return jsonify({
            "id": task_row[0],
            "project_id": task_row[1],
            "name": task_row[2],
            "description": task_row[3],
            "reporter_id": task_row[4],
            "assignee_id": task_row[5],
            "created_at": str(task_row[6]),
            "status": task_row[7],
            "sprint_id": task_row[8],
            "story_points": task_row[9]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/tasks/<int:task_id>", methods=['DELETE'])
@requires_auth
@log_action('TASK')
def delete_task(task_id):
    try:
        was_deleted = delete_task_from_db(task_id)
        
        if not was_deleted:
            return jsonify({"error": "Task card not found"}), 404
            
        return jsonify({"task_id": task_id, "message": f"Task {task_id} deleted cleanly"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route("/tasks/<int:task_id>/assign", methods=['PATCH'])
@requires_auth
@log_action('TASK')
def assign_task(task_id):
    data = request.get_json() or {}
    assignee_id = data.get('assignee_id')

    if not assignee_id:
        return jsonify({"error": "Assignee ID is required"}), 400

    if not get_task(task_id):
        return jsonify({"error": "Task card not found"}), 404
    
    user_exists = check_user_exists_globally(assignee_id)
    if not user_exists:
        return jsonify({"error": "User does not exist"}), 400
   
    try:
        update_task_assignee(task_id, assignee_id)
        return jsonify({"task_id": task_id, "assignee_id": assignee_id, "message": "Task assigned successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

TASK_TRANSITIONS = {
    'OPEN': ['IN PROGRESS', 'ON HOLD', 'VOID'],
    'IN PROGRESS': ['ON HOLD', 'DONE', 'VOID'],
    'ON HOLD': ['OPEN', 'IN PROGRESS', 'VOID'],
    'DONE': ['OPEN'],
    'VOID': []
}

@tasks_bp.route("/tasks/<int:task_id>/status", methods=['PATCH'])
@requires_auth
@log_action('TASK')
def update_status(task_id):
    data = request.get_json() or {}
    target_status = data.get('status')

    if not target_status:
        return jsonify({"error": "Status parameter is required"}), 400

    task_row = get_task(task_id)
    if task_row is None:
        return jsonify({"error": "Task not found"}), 404

    current_status = task_row[7]
    allowed_transitions = TASK_TRANSITIONS.get(current_status, [])
    if target_status not in allowed_transitions:
            return jsonify({"error": "This transition is not allowed"}), 400
    
    try:
        update_task_status(task_id, target_status)
        return jsonify({"task_id": task_id, "status": target_status, "message": "Task timeline advanced"}), 200
    except Exception as e:
            return jsonify({"error": str(e)}), 500

# TODO: What will happen if story points are updated when task is already in sprint.
@tasks_bp.route("/tasks/<int:task_id>/story-points", methods=['PATCH'])
@requires_auth
@log_action('TASK')
def update_story_points(task_id):
    data = request.get_json() or {}
    story_points = data.get('story_points')

    if story_points is None:
        return jsonify({"error": "Story Points parameter is required"}), 400

    task_row = get_task(task_id)
    if task_row is None:
        return jsonify({"error": "Task not found"}), 404

    try:
        update_task_story_points(task_id, story_points)
        return jsonify({"task_id": task_id, "story_points": story_points, "message": "Task story points assigned"}), 200
    except Exception as e:
            return jsonify({"error": str(e)}), 500

@tasks_bp.route("/tasks", methods=['GET'])
def fetch_projects():
    try:
        project_id = request.args.get("projectId")

        if not project_id:
            return jsonify({"error": "Project id is required"}), 400

        status = request.args.get("status")
        page_num = request.args.get("page") or 1
        page_size = request.args.get("pageSize") or 10

        projects = fetch_task_list(project_id, status, page_num, page_size)
        return jsonify({"projects": projects}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500