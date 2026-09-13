from functools import wraps
from flask import request, jsonify, g
from repository.user_repo import get_user

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_email = request.headers.get('X-User-Email')

        if not user_email:
            return jsonify({"error": "Unauthorized: Missing identity header"}), 401

        user_row = get_user(user_email)
        if user_row is None:
            return jsonify({"error": "Forbidden: User profile not registered"}), 403

        g.current_user_id = user_row[0]
        g.current_user_role = user_row[3]

        return f(*args, **kwargs)

    return decorated_function

def require_role(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user_role'):
                return jsonify({"error": "Internal Error: Identity guard missing"}), 500
                
            if g.current_user_role not in allowed_roles:
                return jsonify({
                    "error": f"Forbidden: This action requires one of the following roles: {allowed_roles}. Your role: {g.current_user_role}"
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator