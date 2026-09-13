from flask import Blueprint, request, jsonify
from repository.project_repo import create_project, get_project, remove_project
from middlewares.auth import requires_auth, require_role

projects_bp = Blueprint('projects_bp', __name__)

@projects_bp.route("/projects", methods=['POST'])
@requires_auth
@require_role('PM')
def post_project():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name or not description:
        return jsonify({"error": "name and description are required"}), 400

    try:
        new_project_id = create_project(name, description)
        return jsonify({"id": new_project_id, "message": f"Project {name} created"}), 201
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
def delete_user(project_id):
    try:
        deleted = remove_project(project_id)
        
        if not deleted:
            return jsonify({"error": "User profile not found"}), 404
            
        return jsonify({"message": f"User {project_id} offboarded and deleted cleanly"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500