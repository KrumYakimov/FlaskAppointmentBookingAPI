from typing import Dict, Any, Optional, List

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth_manager import AuthManager, auth
from models import UserModel, ServiceProviderModel, owner_service_provider_association
from models.emums import RoleType
from utils.custom_validators import UniqueConstraintValidator


class UserManager:
    INVALID_USERNAME_OR_PASSWORD_MESSAGE = "Invalid username or password"
    EMAIL_ALREADY_IN_USE_MESSAGE = "Email is already in use"

    @staticmethod
    def register(client_data: Dict[str, Any]) -> str:
        """
        Registers a new client and hashes the password.

        :param client_data: Dictionary containing client details (e.g., email, password).
        :return: The JWT token for the registered client.
        :raises IntegrityError: If there's a database error due to unique constraints.
        """

        client_data["password"] = generate_password_hash(
            client_data["password"], method="pbkdf2:sha256"
        )
        client_data["role"] = RoleType.CLIENT.name

        client = UserModel(**client_data)

        validator = UniqueConstraintValidator(db.session)

        try:
            db.session.add(client)
            db.session.flush()
            return AuthManager.encode_token(client)
        except IntegrityError as e:
            validator.rollback()
            validator.check_unique_violation(e)

    @staticmethod
    def login(data: Dict[str, Any]) -> str:
        """
        Authenticates a user by checking the email and password.

        :param data: Dictionary containing 'email' and 'password'.
        :return: A JWT token as a string for the logged-in user.
        :raises Unauthorized: If the email or password is incorrect.
        """

        user = db.session.execute(
            db.select(UserModel).filter_by(email=data["email"], is_active=True)
        ).scalar()
        if not user or not check_password_hash(user.password, data["password"]):
            raise Unauthorized(UserManager.INVALID_USERNAME_OR_PASSWORD_MESSAGE)
        return AuthManager.encode_token(user)

    @staticmethod
    def change_password(pass_data: Dict[str, Any]) -> None:
        """
        Changes the password of the currently authenticated user.

        :param pass_data: Dictionary containing 'old_password' and 'new_password'.
        :raises BadRequest: If the old password is incorrect.
        """
        user = auth.current_user()

        if not check_password_hash(user.password, pass_data["old_password"]):
            raise BadRequest("Invalid password")

        user.password = generate_password_hash(
            pass_data["new_password"], method="pbkdf2:sha256"
        )
        db.session.add(user)
        db.session.flush()

    @staticmethod
    def get_client_profile(current_user: UserModel) -> UserModel:
        """
        Retrieves the profile of the logged-in client.

        :param current_user: The currently authenticated user (instance of UserModel).
        :return: The user's profile data.
        :raises NotFound: If the user does not exist.
        """

        client_profile = db.session.execute(
            db.select(UserModel).filter_by(id=current_user.id, role=RoleType.CLIENT)
        ).scalar_one_or_none()

        if not client_profile:
            raise NotFound("Client profile not found.")

        return client_profile

    @staticmethod
    def update_user_profile(user: UserModel, data: Dict[str, Any]) -> None:
        """
        Updates the attributes of the given user.

        :param user: The user object to be updated.
        :param data: Dictionary containing updated user fields.
        :raises IntegrityError: If a unique constraint is violated.
        """
        user.email = data.get("email", user.email)
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.phone = data.get("phone", user.phone)

        validator = UniqueConstraintValidator(db.session)

        try:
            db.session.add(user)
            db.session.flush()
        except IntegrityError as e:
            validator.rollback()
            validator.check_unique_violation(e)

    @staticmethod
    def edit_client_profile(
        current_user: UserModel, client_data: Dict[str, Any]
    ) -> None:
        """
        Edits the profile of the current user (client).

        :param current_user: The user object of the current client.
        :param client_data: Dictionary containing updated client fields.
        """
        UserManager.update_user_profile(current_user, client_data)

    @staticmethod
    def deactivate_client(current_user: UserModel) -> None:
        """
        Deactivates the current client.

        :param current_user: The user object of the current client.
        """
        UserManager._deactivate_user(current_user)

    @staticmethod
    def register_user(current_user: UserModel, user_data: Dict[str, Any]) -> str:
        """
        Registers a new user (staff or owner) and hashes the password.

        :param current_user: The user object of the current client (who is registering a user).
        :param user_data: Dictionary containing new user details (email, password, etc.).
        :return: The role of the newly created user.
        :raises NotFound: If associated service providers are not found.
        :raises IntegrityError: If a unique constraint is violated.
        """
        user_data["password"] = generate_password_hash(
            user_data["password"], method="pbkdf2:sha256"
        )

        new_user = UserModel(
            email=user_data["email"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            phone=user_data["phone"],
            role=user_data["role"],
        )

        validator = UniqueConstraintValidator(db.session)

        try:
            if new_user.role == RoleType.STAFF.name:
                service_provider = db.session.execute(
                    db.select(ServiceProviderModel).filter_by(
                        id=user_data["service_provider_id"]
                    )
                ).scalar_one_or_none()
                if not service_provider:
                    raise NotFound(
                        f"Service Provider with ID {user_data['service_provider_id']} not found."
                    )
                new_user.service_provider_id = service_provider.id
            elif new_user.role == RoleType.OWNER.name:
                service_provider_ids = user_data.get("owned_company_ids", [])
                for sp_id in service_provider_ids:
                    service_provider = db.session.execute(
                        db.select(ServiceProviderModel).filter_by(id=sp_id)
                    ).scalar_one_or_none()
                    if not service_provider:
                        raise NotFound(f"Service Provider with ID {sp_id} not found.")
                    new_user.owned_companies.append(service_provider)
            db.session.add(new_user)
            db.session.flush()
            return new_user.role
        except IntegrityError as e:
            validator.rollback()
            validator.check_unique_violation(e)

    @staticmethod
    def get_users(
        current_user: UserModel,
        status: Optional[str] = None,
        user_number: Optional[int] = None,
    ) -> List[UserModel]:
        """
        Retrieves a list of users relative to the current user's rights.

        :param current_user: The currently authenticated user.
        :param status: Optional status filter (e.g., active/inactive).
        :param user_number: Optional specific user ID to retrieve.
        :return: A list of users matching the criteria.
        """

        stmt = db.select(UserModel).distinct()

        if current_user.role == RoleType.OWNER:
            stmt = (
                db.select(UserModel)
                .distinct()
                .join(
                    owner_service_provider_association,
                    owner_service_provider_association.c.owner_id == current_user.id,
                )
                .join(
                    ServiceProviderModel,
                    owner_service_provider_association.c.service_provider_id
                    == ServiceProviderModel.id,
                )
                .where(UserModel.role == RoleType.STAFF)
                .where(
                    UserModel.service_provider_id
                    == owner_service_provider_association.c.service_provider_id
                )
            )

        elif current_user.role == RoleType.APPROVER:
            stmt = stmt.where(UserModel.role.in_([RoleType.OWNER, RoleType.STAFF]))

        if user_number:
            stmt = stmt.where(UserModel.id == user_number)

        if status:
            is_active = status.lower() == "active"
            stmt = stmt.where(UserModel.is_active == is_active)

        users = db.session.execute(stmt).scalars().all()

        return users

    @staticmethod
    def edit_user_profile(user_data: Dict[str, Any], user_id: int) -> None:
        """
        Edits the profile of the user with the given user ID.

        :param user_data: Dictionary containing updated user fields.
        :param user_id: ID of the user to be updated.
        :raises NotFound: If the user with the given ID is not found.
        """
        user = db.session.execute(
            db.select(UserModel).filter_by(id=user_id)
        ).scalar_one_or_none()

        if not user:
            raise NotFound(f"User with id {user_id} not found.")

        UserManager.update_user_profile(user, user_data)

    @staticmethod
    def deactivate_user(user_id: int) -> None:
        """
        Deactivates a user by their ID.

        :param user_id: The ID of the user to deactivate.
        :raises NotFound: If the user with the given ID is not found.
        """
        user = db.session.execute(
            db.select(UserModel).filter_by(id=user_id)
        ).scalar_one_or_none()

        if not user:
            raise NotFound(f"User with id {user_id} not found.")

        UserManager._deactivate_user(user)

    # Soft deletion: Deactivate the account and mask sensitive data
    @staticmethod
    def _deactivate_user(user: UserModel) -> None:
        """
        Deactivates the account and masks sensitive user data.

        :param user: The user object to deactivate.
        """
        user.is_active = False
        user.first_name = "Deactivated"
        user.last_name = "User"
        user.email = f"deactivated_user_{user.id}@example.com"
        user.phone = f"000000000{user.id}"
        db.session.add(user)
        db.session.flush()
