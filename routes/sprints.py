from flask import Blueprint, request, jsonify, g
from middlewares.auth import requires_auth, require_role
from repository.sprints_repo import create_sprint, get_sprint, update_sprint_status_in_db, get_sprint_current_weight, assign_task_to_sprint
from repository.task_repo import get_task

sprints_bp = Blueprint('sprints_bp', __name__)

@sprints_bp.route("/sprints", methods=['POST'])
@requires_auth
@require_role('PM')
def post_sprint():
    data = request.get_json() or {}
    project_id = data.get('project_id')
    name = data.get('name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    max_capacity = data.get('max_capacity')

    if not project_id or not name or not start_date or not end_date or not max_capacity:
        return jsonify({"error": "All sprint planning fields are required"}), 400

    try:
        new_sprint_id = create_sprint(project_id, name, start_date, end_date, max_capacity)
        return jsonify({"id": new_sprint_id, "message": f"Sprint created with max capacity of {max_capacity} points"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sprints_bp.route("/sprints/<int:sprint_id>", methods=['GET'])
@requires_auth
def get_sprint_profile(sprint_id):
    try:
        sprint_row = get_sprint(sprint_id)
        
        if sprint_row is None:
            return jsonify({"error": "Sprint not found"}), 404
            
        return jsonify({
            "id": sprint_row[0],
            "project_id": sprint_row[1],
            "name": sprint_row[2],
            "start_date": sprint_row[3],
            "end_date": sprint_row[4],
            "max_capacity": sprint_row[5],
            "status": str(sprint_row[6]),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sprints_bp.route("/sprints/<int:sprint_id>/current-weight", methods=['GET'])
@requires_auth
def get_sprint_weight(sprint_id):
    try:
        sprint_weight = get_sprint_current_weight(sprint_id)
        
        if sprint_weight is None:
            return jsonify({"error": "Sprint not found"}), 404
            
        return jsonify({"current_weight": sprint_weight}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sprints_bp.route("/sprints/<int:sprint_id>/add-task", methods=['PATCH'])
@requires_auth
@require_role('PM') 
def add_task_to_sprint(sprint_id):
    data = request.get_json() or {}
    task_id = data.get('task_id')

    if not task_id:
        return jsonify({"error": "Task ID parameter is required"}), 400

    sprint_row = get_sprint(sprint_id)
    if not sprint_row:
        return jsonify({"error": "Sprint container not found"}), 404

    task_row = get_task(task_id)
    if not task_row:
        return jsonify({"error": "Task card not found"}), 404

    sprint_max_capacity = sprint_row[5] 
    task_weight = task_row[8] if task_row[8] else 0 
    current_sprint_weight = get_sprint_current_weight(sprint_id)

    if (current_sprint_weight + task_weight > sprint_max_capacity):
        return jsonify({"error": "Current Sprint is Overloaded. Can't add another task."}), 400
    
    try:
        assign_task_to_sprint(task_id, sprint_id)
        return jsonify({"task_id": task_id, "sprint_id": sprint_id, "message": "Task successfully locked into sprint schedule"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

SPRINT_TRANSITIONS = {
    'PLANNING': ['ACTIVE'],
    'ACTIVE': ['COMPLETED'],
    'COMPLETED': []
}

@sprints_bp.route("/sprints/<int:sprint_id>/status", methods=['PATCH'])
@requires_auth
@require_role('PM') 
def update_sprint_status(sprint_id):
    data = request.get_json() or {}
    target_status = data.get('status')

    if not sprint_id:
        return jsonify({"error": "Sprint ID parameter is required"}), 400

    sprint_row = get_sprint(sprint_id)
    if not sprint_row:
        return jsonify({"error": "Sprint container not found"}), 404

    current_status = sprint_row[6]
    allowed_transitions = SPRINT_TRANSITIONS.get(current_status, [])

    if target_status not in allowed_transitions:
        return jsonify({"error": "This transition is not allowed."}), 400
    
    try:
        update_sprint_status_in_db(sprint_id, target_status)
        return jsonify({"sprint_id": sprint_id, "status": target_status, "message": "Sprint advanced"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500