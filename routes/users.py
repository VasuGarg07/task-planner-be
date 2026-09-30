from flask import Blueprint, request, jsonify
from repository.user_repo import create_user, fetch_user_list, get_user, remove_user

users_bp = Blueprint('users_bp', __name__)

@users_bp.route("/users", methods=['POST'])
def post_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    role = data.get('role', 'BA')

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    try:
        new_user_id = create_user(username, email, role)
        return jsonify({"id": new_user_id, "message": "User onboarding complete"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/users", methods=['GET'])
def get_user_profile():
    try:
        # 1. Fetch User Profile 
        email = request.args.get('email')
        if email:
            user_row = get_user(email)
            
            if user_row is None:
                return jsonify({"error": "User profile not found"}), 404
                
            return jsonify({
                "id": user_row[0],
                "username": user_row[1],
                "email": user_row[2],
                "role": user_row[3]
            }), 200

        # 2. Fetch User List
        page_num = request.args.get("page") or 1
        page_size = request.args.get("pageSize") or 10

        users = fetch_user_list(page_num, page_size)
        return jsonify({"users": users}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/users/<int:user_id>", methods=['DELETE'])
def delete_user(user_id):
    try:
        deleted = remove_user(user_id)
        
        if not deleted:
            return jsonify({"error": "User profile not found"}), 404
            
        return jsonify({"message": f"User {user_id} offboarded and deleted cleanly"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500