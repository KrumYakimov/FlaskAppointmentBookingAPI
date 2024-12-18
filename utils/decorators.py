from functools import wraps

from flask import request
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Forbidden, Unauthorized

from managers.auth_manager import auth
from models import RoleType, UserModel
from utils.role_permitions import ROLE_PERMISSIONS


def permission_required(*required_roles):
    """
    Decorator to enforce role-based access control on Flask views.
    :param required_roles: Roles that are allowed to access the decorated function.
    :raises Unauthorized: If the user is not authenticated.
    :raises Forbidden: If the user does not have the required role.
    """

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
    """
    Decorator to validate incoming request data against a Marshmallow schema.
    :param schema_name: The schema class to validate against.
    :raises BadRequest: If the request payload is missing, not JSON, or does not match the schema.
    """

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


def role_based_access_control(action: str):
    """
    Decorator for role-based access control on actions performed on users.
    :param action: The action being performed (e.g., 'view', 'edit', 'deactivate').
    :raises Forbidden: If the user does not have permission for the action.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = auth.current_user()

            target_user_id = kwargs.get("user_id", None)
            target_user = None

            if target_user_id:
                target_user = UserModel.query.get(target_user_id)

            if not target_user and action in ["create", "edit", "deactivate"]:
                target_role = request.json.get("role", None)
            else:
                target_role = target_user.role.name if target_user else None

            user_role = (
                current_user.role.name
                if isinstance(current_user.role, RoleType)
                else current_user.role
            )

            allowed_roles = ROLE_PERMISSIONS.get(user_role, {}).get(action, [])

            if target_role and target_role.upper() not in allowed_roles:
                raise Forbidden(
                    f"You do not have permission to {action} users with the role {target_role}."
                )

            if (
                action in ["view", "edit", "deactivate"]
                and user_role == "OWNER"
                and target_user
            ):
                owned_service_provider_ids = {
                    sp.id for sp in current_user.owned_companies
                }

                if target_user.service_provider_id not in owned_service_provider_ids:
                    raise Forbidden(
                        f"You can only {action} staff from your own service provider."
                    )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def make_optional(schema_cls):
    """Decorator to make all fields in a schema optional without overriding validation logic."""
    for field_name, field in schema_cls._declared_fields.items():
        if field.required:
            field.required = False
    return schema_cls
