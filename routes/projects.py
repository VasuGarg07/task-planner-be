from flask import Blueprint, request, jsonify
from repository.project_repo import create_project, get_project, remove_project, update_project_status_in_db
from middlewares.auth import requires_auth, require_role
from middlewares.logger import log_action

projects_bp = Blueprint('projects_bp', __name__)

@projects_bp.route("/projects", methods=['POST'])
@requires_auth
@require_role('PM')
@log_action('PROJECT')
def post_project():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name or not description:
        return jsonify({"error": "name and description are required"}), 400

    try:
        new_project_id = create_project(name, description)
        return jsonify({"project_id": new_project_id, "message": f"Project {name} created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route("/projects/<int:project_id>", methods=['GET'])
@requires_auth
def get_project_profile(project_id):
    try:
        project_row = get_project(project_id)
        
        if project_row is None:
            return jsonify({"error": "Project not found"}), 404
            
        return jsonify({
            "id": project_row[0],
            "name": project_row[1],
            "description": project_row[2],
            "created_at": str(project_row[3]),
            "status": project_row[4]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route("/projects/<int:project_id>", methods=['DELETE'])
@requires_auth
@require_role('PM')
@log_action('PROJECT')
def delete_project(project_id):
    try:
        deleted = remove_project(project_id)
        
        if not deleted:
            return jsonify({"error": "Project not found"}), 404
            
        return jsonify({"project_id": project_id, "message": f"Project {project_id} deleted cleanly"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

PROJECT_TRANSITIONS = {
    'NOT STARTED': ['DISCOVERY', 'DROPPED'],
    'DISCOVERY': ['IN PROGRESS', 'ON HOLD', 'DROPPED'],
    'IN PROGRESS': ['ON HOLD', 'COMPLETED', 'DROPPED'],
    'ON HOLD': ['IN PROGRESS', 'DISCOVERY', 'DROPPED'],
    'COMPLETED': [],
    'DROPPED': []
}

@projects_bp.route("/projects/<int:project_id>/status", methods=['PATCH'])
@requires_auth
@require_role('PM')
@log_action('PROJECT')
def update_status(project_id):
    data = request.get_json() or {}
    target_status = data.get('status')

    if not target_status:
        return jsonify({"error": "Status parameter is required"}), 400

    project_row = get_project(project_id)
    if project_row is None:
        return jsonify({"error": "Project not found"}), 404

    current_status = project_row[4]
    allowed_transitions = PROJECT_TRANSITIONS.get(current_status, [])

    if target_status not in allowed_transitions:
        return jsonify({"error": "This transition is not allowed"}), 400

    try:
        update_project_status_in_db(project_id, target_status)
        return jsonify({"project_id": project_id, "status": target_status, "message": "Project timeline advanced"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
