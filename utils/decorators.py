from functools import wraps

from flask import request
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Forbidden, Unauthorized

from db import db
from managers.auth_manager import auth
from models import RoleType, UserModel
from utils.role_permitions import ROLE_PERMISSIONS


def permission_required(*required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = auth.current_user()

            if not current_user:
                raise Unauthorized("Authentication is required to access this resource")

            if current_user.role not in required_roles:
                raise Forbidden("You do not have permissions to access this resource")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_schema(schema_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            schema = schema_name()
            try:
                data = request.get_json()
                if data is None:
                    raise BadRequest("Request payload is missing or not JSON")
            except Exception as e:
                raise BadRequest(f"Invalid JSON format: {e}")

            errors = schema.validate(data)
            if errors:
                raise BadRequest(f"Invalid payload: {errors}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


# def role_based_access_control(action):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             current_user = auth.current_user()
#             target_role = request.json.get('role', None)  # The role being registered or edited
#
#             # Get current user's role
#             user_role = current_user.role.name if isinstance(current_user.role, RoleType) else current_user.role
#
#             # Get the allowed roles for the given action (register, edit, deactivate)
#             allowed_roles = ROLE_PERMISSIONS.get(user_role, {}).get(action, [])
#
#             # Check if the target role is in the allowed roles for this action
#             if target_role and target_role.upper() not in allowed_roles:
#                 raise Forbidden(f"You do not have permission to {action} users with the role {target_role}.")
#
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator


# def role_based_access_control(action):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             current_user = auth.current_user()
#
#             # Fetch the target user by ID if passed in kwargs (e.g., for edit, view, deactivate)
#             target_user_id = kwargs.get('user_id', None)
#             target_user = None
#             if target_user_id:
#                 target_user = UserModel.query.get(target_user_id)
#
#             # If no target user is passed and the action requires it (register, edit), get the role from the request
#             if not target_user and action in ['register', 'edit', 'deactivate']:
#                 target_role = request.json.get('role', None)
#             else:
#                 target_role = target_user.role.name if target_user else None
#
#             # Get current user's role
#             user_role = current_user.role.name if isinstance(current_user.role, RoleType) else current_user.role
#
#             # Fetch the allowed roles for the current action
#             allowed_roles = ROLE_PERMISSIONS.get(user_role, {}).get(action, [])
#
#             # Validate that the current user has permission to perform the action on the target role
#             if target_role and target_role.upper() not in allowed_roles:
#                 raise Forbidden(f"You do not have permission to {action} users with the role {target_role}.")
#
#             # Additional logic for Owners viewing their staff only from their own service provider
#             if action == 'view' and user_role == 'OWNER':
#                 # Ensure the owner is only viewing staff from their own service provider
#                 if target_user and target_user.service_provider_id != current_user.service_provider_id:
#                     raise Forbidden("You can only view staff from your own service provider.")
#
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator

def role_based_access_control(action):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = auth.current_user()

            # Fetch the target user by ID if passed in kwargs (e.g., for edit, view, deactivate)
            target_user_id = kwargs.get('user_id', None)
            target_user = None
            if target_user_id:
                target_user = UserModel.query.get(target_user_id)

                # Add the print statement here to debug the roles
            if target_user:
                print(f"Current User Role: {current_user.role}, Target User Role: {target_user.role}")
            else:
                print(f"Current User Role: {current_user.role}, No Target User Found")

            # If no target user is passed and the action requires it (register, edit), get the role from the request
            if not target_user and action in ['register', 'edit', 'deactivate']:
                target_role = request.json.get('role', None)
            else:
                target_role = target_user.role.name if target_user else None

            # Get current user's role
            user_role = current_user.role.name if isinstance(current_user.role, RoleType) else current_user.role

            # Fetch the allowed roles for the current action
            allowed_roles = ROLE_PERMISSIONS.get(user_role, {}).get(action, [])

            # Validate that the current user has permission to perform the action on the target role
            if target_role and target_role.upper() not in allowed_roles:
                raise Forbidden(f"You do not have permission to {action} users with the role {target_role}.")

            # Additional logic for Owners managing (view, edit, deactivate) their staff only
            if action in ['view', 'edit', 'deactivate'] and user_role == 'OWNER' and target_user:
                # Ensure the owner is only managing staff from their own service provider
                owned_service_provider_ids = {sp.id for sp in current_user.owned_companies}

                # Check if the target user's service provider is among the ones the owner manages
                if target_user.service_provider_id not in owned_service_provider_ids:
                    raise Forbidden(f"You can only {action} staff from your own service provider.")

            return func(*args, **kwargs)
        return wrapper
    return decorator










# def ownership_required(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         current_user = auth.current_user()
#         target_user = kwargs.get('user')
#
#         # Check if the current user is allowed to manage this resource (e.g., staff)
#         if current_user.role in RoleType.OWNER and target_user.role == RoleType.STAFF:
#             if not current_user.owned_companies.contains(target_user.service_provider):
#                 raise Forbidden("You do not have permission to manage this staff member.")
#
#         return func(*args, **kwargs)
#
#     return wrapper

