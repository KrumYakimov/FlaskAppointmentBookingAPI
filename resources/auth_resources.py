from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.user_manager import UserManager
from models import RoleType
from schemas.request.user_request_schemas import (
    ClientRegistrationRequestSchema,
    UserLoginRequestSchema,
    PasswordChangeSchema,
    UserEditRequestSchema,
    UserRegistrationRequestSchema,
)
from schemas.response.user_response_schemas import (
    ClientResponseSchema,
    UserResponseSchema,
)
from utils.decorators import (
    validate_schema,
    permission_required,
    role_based_access_control,
)


class ClientRegistration(Resource):
    @validate_schema(ClientRegistrationRequestSchema)
    def post(self):
        data = request.get_json()
        token = UserManager.register(data)
        return {"token": token}, 201


class Login(Resource):
    @validate_schema(UserLoginRequestSchema)
    def post(self):
        data = request.get_json()
        token = UserManager.login(data)
        return {"token": token}

# TODO: POST for user logout (Logout, "logout/")


class ChangePassword(Resource):
    @auth.login_required
    @validate_schema(PasswordChangeSchema)
    def post(self):
        data = request.get_json()
        UserManager.change_password(data)
        return {"message": "Password changed successfully"}, 200


class ClientProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def get(self):
        current_user = auth.current_user()
        profile = UserManager.get_client_profile(current_user)
        return {"profile": ClientResponseSchema().dump(profile)}, 200


class ClientEditing(Resource):
    @auth.login_required
    @validate_schema(UserEditRequestSchema)
    @permission_required(RoleType.CLIENT)
    def put(self):
        data = request.get_json()
        current_user = auth.current_user()
        UserManager.edit_client_profile(current_user, data)
        return {"message": "Account edited successfully."}, 200


class ClientDeactivation(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def put(self):
        current_user = auth.current_user()
        UserManager.deactivate_client(current_user)
        return {"message": "Account deactivated successfully."}, 200


class UserRegistration(Resource):
    @auth.login_required
    @validate_schema(UserRegistrationRequestSchema)
    @role_based_access_control("create")
    def post(self):
        current_user = auth.current_user()
        user_data = request.get_json()
        role = UserManager.register_user(current_user, user_data)
        return {
            "message": f"A user with the role of {role} has been registered successfully."
        }, 201


class UserProfile(Resource):
    @auth.login_required
    @role_based_access_control("view")
    def get(self, status=None, user_id=None):
        current_user = auth.current_user()
        status = status or request.args.get("status", None)
        user_number = user_id or request.args.get("user_number", None)
        users = UserManager.get_users(
            current_user, status=status, user_number=user_number
        )
        return {"users": UserResponseSchema().dump(users, many=True)}, 200


class UserEditing(Resource):
    @auth.login_required
    @validate_schema(UserEditRequestSchema)
    @role_based_access_control("edit")
    def put(self, user_id):
        data = request.get_json()
        UserManager.edit_user_profile(data, user_id)
        return {"message": "Account edited successfully."}, 200


class UserDeactivation(Resource):
    @auth.login_required
    @role_based_access_control("deactivate")
    def put(self, user_id):
        UserManager.deactivate_user(user_id)
        return {"message": "Account deactivated successfully."}, 200
