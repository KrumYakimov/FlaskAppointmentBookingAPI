from typing import Optional

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
    def post(self) -> tuple:
        """
        Registers a new client and returns a token.

        :return: A tuple containing the token and a 201 status code.
        """
        data = request.get_json()
        token = UserManager.register(data)
        return {"token": token}, 201


class Login(Resource):
    @validate_schema(UserLoginRequestSchema)
    def post(self) -> dict[str, str]:
        """
        Authenticates a user and returns a token.

        :return: A tuple containing the token.
        :raises Unauthorized: If the email or password is incorrect.
        """
        data = request.get_json()
        token = UserManager.login(data)
        return {"token": token}

# TODO: POST for user logout (Logout, "logout/")


class ChangePassword(Resource):
    @auth.login_required
    @validate_schema(PasswordChangeSchema)
    def post(self) -> tuple:
        """
        Changes the password for the authenticated user.

        :return: A message indicating successful password change and a 200 status code.
        """
        data = request.get_json()
        UserManager.change_password(data)
        return {"message": "Password changed successfully"}, 200


class ClientProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def get(self) -> tuple:
        """
        Retrieves the profile of the authenticated client.

        :return: A tuple containing the client's profile data and a 200 status code.
        """
        current_user = auth.current_user()
        profile = UserManager.get_client_profile(current_user)
        return {"profile": ClientResponseSchema().dump(profile)}, 200


class ClientEditing(Resource):
    @auth.login_required
    @validate_schema(UserEditRequestSchema)
    @permission_required(RoleType.CLIENT)
    def put(self) -> tuple:
        """
        Edits the profile of the authenticated client.

        :return: A message indicating successful account edit and a 200 status code.
        """
        data = request.get_json()
        current_user = auth.current_user()
        UserManager.edit_client_profile(current_user, data)
        return {"message": "Account edited successfully."}, 200


class ClientDeactivation(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def put(self) -> tuple:
        """
        Deactivates the authenticated client's account.

        :return: A message indicating successful account deactivation and a 200 status code.
        """
        current_user = auth.current_user()
        UserManager.deactivate_client(current_user)
        return {"message": "Account deactivated successfully."}, 200


class UserRegistration(Resource):
    @auth.login_required
    @validate_schema(UserRegistrationRequestSchema)
    @role_based_access_control("create")
    def post(self) -> tuple:
        """
        Registers a new user (staff or owner).

        :return: A message indicating successful user registration and a 201 status code.
        """
        current_user = auth.current_user()
        user_data = request.get_json()
        role = UserManager.register_user(current_user, user_data)
        return {
            "message": f"A user with the role of {role} has been registered successfully."
        }, 201


class UserProfile(Resource):
    @auth.login_required
    @role_based_access_control("view")
    def get(self, status: Optional[str] = None, user_id: Optional[int] = None) -> tuple:
        """
        Retrieves users relative to the current user's rights.

        :param status: Optional status filter for users.
        :param user_id: Optional specific user ID to retrieve.
        :return: A tuple containing the list of users and a 200 status code.
        """
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
    def put(self, user_id: int) -> tuple:
        """
        Edits the profile of a user with the given user ID.

        :param user_id: The ID of the user to be updated.
        :return: A message indicating successful account edit and a 200 status code.
        :raises NotFound: If the user with the given ID is not found.
        """
        data = request.get_json()
        UserManager.edit_user_profile(data, user_id)
        return {"message": "Account edited successfully."}, 200


class UserDeactivation(Resource):
    @auth.login_required
    @role_based_access_control("deactivate")
    def put(self, user_id: int) -> tuple:
        """
        Deactivates a user by their ID.

        :param user_id: The ID of the user to deactivate.
        :return: A message indicating successful account deactivation and a 200 status code.
        :raises NotFound: If the user with the given ID is not found.
        """
        UserManager.deactivate_user(user_id)
        return {"message": "Account deactivated successfully."}, 200
