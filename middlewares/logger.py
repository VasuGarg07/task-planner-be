from functools import wraps
from flask import g, request
from repository.log_repo import get_subject_project, create_log

ACTION_TYPE_MAP = {
    "POST": "CREATE",
    "PUT": "UPDATE",
    "PATCH": "UPDATE",
    "DELETE": "DELETE",
}


def log_action(subject_type='TASK'):
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            response, status = f(*args, **kwargs)

            if status == 200 or status == 201:
                actor_id = g.current_user_id
                action_type = ACTION_TYPE_MAP[request.method]
                res_dict = response.get_json()

                if subject_type == 'PROJECT':
                    subject_id = res_dict.get('project_id')
                    project_id = subject_id
                elif subject_type == 'SPRINT':
                    subject_id = res_dict.get('sprint_id')
                    project_id = get_subject_project(subject_type, subject_id)
                elif subject_type == 'TASK':
                    subject_id = res_dict.get('task_id')
                    project_id = get_subject_project(subject_type, subject_id)
    
                print("RequestDetails - ", request.view_args)
    
                create_log(project_id, actor_id, subject_type, subject_id, action_type, res_dict)

            return response, status

        return decorated_function
    
    return decorator