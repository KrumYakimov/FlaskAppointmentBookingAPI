from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound, Forbidden
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
    def register(client_data: dict) -> str:
        """
        Hashes the plain password

        :param client_data: dict containing client details (e.g., email, password).
        :return: client
        :raises InternalServerError: If there's a database error.
        """

        client_data["password"] = generate_password_hash(client_data['password'], method='pbkdf2:sha256')
        client_data["role"] = RoleType.CLIENT.name
        print(client_data)
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
    def login(data: dict) -> str:
        """
        Checks the email and password (hashes the plain password)

        :param data: dict containing 'email' and 'password'.
        :return: A JWT token as a string for the logged-in user.
        :raises Unauthorized: If the email or password is incorrect.
        """

        user = db.session.execute(db.select(UserModel).filter_by(email=data["email"], is_active=True)).scalar()
        if not user or not check_password_hash(user.password, data["password"]):
            raise Unauthorized(UserManager.INVALID_USERNAME_OR_PASSWORD_MESSAGE)
        return AuthManager.encode_token(user)

    @staticmethod
    def change_password(pass_data: dict) -> None:
        user = auth.current_user()

        if not check_password_hash(user.password, pass_data["old_password"]):
            raise BadRequest("Invalid password")

        user.password = generate_password_hash(pass_data["new_password"], method='pbkdf2:sha256')
        db.session.add(user)
        db.session.flush()

    @staticmethod
    def get_client_profile(current_user):
        """
        Retrieves the profile of the logged-in client.

        :param current_user: The currently authenticated user (instance of UserModel)
        :return: The user's profile data
        :raises NotFound: If the user does not exist
        """

        client_profile = db.session.execute(
            db.select(UserModel).filter_by(id=current_user.id, role=RoleType.CLIENT)
        ).scalar_one_or_none()

        if not client_profile:
            raise NotFound("Client profile not found.")

        return client_profile

    @staticmethod
    def update_user_profile(user, data):
        """
        Updates the user attributes and handles uniqueness validation.

        :param user: The user object to be updated
        :param data: Dictionary containing updated user fields
        :raises IntegrityError: If a unique constraint is violated
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
    def edit_client_profile(current_user, client_data):
        """
        Edits the profile of the current user (client).

        :param current_user: The user object of the current client
        :param client_data: Dictionary containing updated client fields
        """
        UserManager.update_user_profile(current_user, client_data)

    @staticmethod
    def deactivate_client(current_user):
        UserManager._deactivate_user(current_user)

    @staticmethod
    def register_user(current_user, user_data):
        user_data["password"] = generate_password_hash(user_data['password'], method='pbkdf2:sha256')


        new_user = UserModel(
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            role=user_data['role']
        )

        validator = UniqueConstraintValidator(db.session)

        try:
            if new_user.role == RoleType.STAFF:
                service_provider = db.session.execute(
                    db.select(ServiceProviderModel).filter_by(id=user_data['service_provider_id'])).scalar_one_or_none()
                if not service_provider:
                    raise NotFound(f"Service Provider with ID {user_data['service_provider_id']} not found.")
                new_user.service_provider_id = service_provider.id
            elif new_user.role == RoleType.OWNER.name:
                service_provider_ids = user_data.get('owned_company_ids', [])
                print(f"Owned company IDs retrieved for owner: {service_provider_ids}")
                for sp_id in service_provider_ids:
                    service_provider = db.session.execute(
                        db.select(ServiceProviderModel).filter_by(id=sp_id)).scalar_one_or_none()
                    if not service_provider:
                        raise NotFound(f"Service Provider with ID {sp_id} not found.")
                    new_user.owned_companies.append(service_provider)
            db.session.add(new_user)
            db.session.flush()
            return new_user.role
        except IntegrityError as e:
            validator.rollback()
            validator.check_unique_violation(e)

    # @staticmethod
    # def get_users(current_user, status=None, user_number=None):
    #     """
    #     Retrieves a list of users relative to the current user's rights.
    #     Can filter by status (active/inactive) or user number.
    #
    #     :param current_user: The currently authenticated user
    #     :param status: 'active' or 'inactive' to filter users
    #     :param user_number: A specific user ID to search for
    #     :return: A list of users
    #     """
    #     stmt = db.select(UserModel)
    #
    #     if current_user.role == RoleType.ADMIN:
    #         pass
    #     elif current_user.role == RoleType.APPROVER:
    #         stmt = stmt.where(UserModel.role.in_([RoleType.OWNER, RoleType.STAFF]))
    #     elif current_user.role == RoleType.OWNER:
    #         # Owners can only view staff from their own service provider
    #         stmt = (
    #             stmt.join(owner_service_provider_association,
    #                       owner_service_provider_association.c.owner_id == UserModel.id)
    #             .where(owner_service_provider_association.c.service_provider_id == current_user.service_provider_id,
    #                    UserModel.role == RoleType.STAFF)
    #         )
    #     else:
    #         raise Forbidden("You do not have permission to view users.")
    #
    #     if user_number:
    #         stmt = stmt.where(UserModel.id == user_number)
    #         result = db.session.execute(stmt)
    #         user = result.scalar_one_or_none()
    #         if not user:
    #             raise NotFound(f"You do not have permission to view {user_number}.")
    #         return [user]
    #
    #     if status:
    #         if status not in ['active', 'inactive']:
    #             raise BadRequest("Invalid status. Allowed values are 'active' or 'inactive'.")
    #         is_active = status == 'active'
    #         stmt = stmt.where(UserModel.is_active == is_active)
    #
    #     result = db.session.execute(stmt)
    #     users = result.scalars().all()
    #     return users



    # @staticmethod
    # def get_users(current_user, status=None, user_number=None):
    #     """
    #     Retrieves a list of users relative to the current user's rights.
    #     Can filter by status (active/inactive) or user number.
    #     """
    #     # Start with the base select query
    #     stmt = db.select(UserModel).distinct()  # Using distinct to avoid duplicates
    #
    #     # Apply role-based filtering
    #     if current_user.role == RoleType.OWNER:
    #         stmt = (
    #             db.select(UserModel)
    #             .distinct()
    #             .join(owner_service_provider_association,
    #                   owner_service_provider_association.c.owner_id == current_user.id)
    #             .join(ServiceProviderModel,
    #                   owner_service_provider_association.c.service_provider_id == ServiceProviderModel.id)
    #             .where(UserModel.role == RoleType.STAFF)
    #             .where(UserModel.service_provider_id == owner_service_provider_association.c.service_provider_id)
    #         )
    #     elif current_user.role == RoleType.APPROVER:
    #         # Use `where()` instead of `filter()` to apply conditions in the new approach
    #         stmt = stmt.where(UserModel.role.in_([RoleType.OWNER, RoleType.STAFF]))
    #
    #     # Apply filters based on user_number
    #     if user_number:
    #         stmt = stmt.where(UserModel.id == user_number)
    #
    #     # Apply filters based on status
    #     if status:
    #         is_active = status.lower() == 'active'
    #         stmt = stmt.where(UserModel.is_active == is_active)
    #
    #     # Execute the query and retrieve the results
    #     users = db.session.execute(stmt).scalars().all()
    #
    #     return users


    @staticmethod
    def get_users(current_user, status=None, user_number=None):
        """
        Retrieves a list of users relative to the current user's rights.
        Can filter by status (active/inactive) or user number.
        """
        # Start with the base select query
        stmt = db.select(UserModel).distinct()

        if current_user.role == RoleType.OWNER:
            # Owner-specific filtering
            stmt = (
                db.select(UserModel)
                .distinct()
                .join(owner_service_provider_association,
                      owner_service_provider_association.c.owner_id == current_user.id)
                .join(ServiceProviderModel,
                      owner_service_provider_association.c.service_provider_id == ServiceProviderModel.id)
                .where(UserModel.role == RoleType.STAFF)
                .where(UserModel.service_provider_id == owner_service_provider_association.c.service_provider_id)
            )
            print(f"SQL Query for OWNER: {stmt}")
        elif current_user.role == RoleType.APPROVER:
            # Approvers can view owners and staff
            stmt = stmt.where(UserModel.role.in_([RoleType.OWNER, RoleType.STAFF]))

        # Apply filters based on user_number
        if user_number:
            stmt = stmt.where(UserModel.id == user_number)

        # Apply filters based on status
        if status:
            is_active = status.lower() == 'active'
            stmt = stmt.where(UserModel.is_active == is_active)

        # Debug before executing query
        print(f"Final SQL Query: {stmt}")

        # Execute the query and retrieve the results
        users = db.session.execute(stmt).scalars().all()

        print(f"Users fetched: {users}")
        return users

    @staticmethod
    def edit_user_profile(user_data, user_id):
        """
        Edits the profile of the user with the given user_id.

        :param user_data: Dictionary containing updated user fields
        :param user_id: ID of the user to be updated
        :raises NotFound: If the user with the given ID is not found
        """
        user = db.session.execute(db.select(UserModel).filter_by(id=user_id)).scalar_one_or_none()

        if not user:
            raise NotFound(f"User with id {user_id} not found.")

        UserManager.update_user_profile(user, user_data)

    @staticmethod
    def deactivate_user(user_id):
        # user_to_deactivate = UserModel.query.filter_by(id=user_id).scalar_one_or_none()
        #
        # if current_user.id == user_to_deactivate.id:
        #     raise Forbidden("You cannot deactivate your own account.")
        #
        # if user_to_deactivate.is_active is False:
        #     raise Forbidden(f"User with ID {user_id} is already deactivated.")
        #
        # # Admins can perform a soft delete on other admins and approvers.
        # if current_user.role == RoleType.ADMIN and user_to_deactivate.role in [
        #     RoleType.ADMIN,
        #     RoleType.APPROVER,
        #     RoleType.OWNER,
        #     RoleType.STAFF,
        #     RoleType.CLIENT
        # ]:
        #     UserManager._deactivate_user(user_to_deactivate)
        #
        # # Approvers can perform a soft delete on owners
        # elif current_user.role == RoleType.APPROVER and user_to_deactivate.role == RoleType.OWNER:
        #     UserManager._deactivate_user(user_to_deactivate)
        #
        # # Owners can perform a soft delete on their staff
        # elif current_user.role == RoleType.OWNER and user_to_deactivate.role == RoleType.STAFF:
        #     UserManager._deactivate_user(user_to_deactivate)
        #
        # else:
        #     raise Forbidden("You do not have permission to deactivate this user.")

        # Retrieve the user from the database using user_id
        user = db.session.execute(db.select(UserModel).filter_by(id=user_id)).scalar_one_or_none()

        if not user:
            raise NotFound(f"User with id {user_id} not found.")

        UserManager._deactivate_user(user)

    # Soft deletion: Deactivate the account and mask sensitive data
    @staticmethod
    def _deactivate_user(user):
        user.is_active = False
        user.first_name = "Deactivated"
        user.last_name = "User"
        user.email = f"deactivated_user_{user.id}@example.com"
        user.phone = f"000000000{user.id}"
        db.session.add(user)
        db.session.flush()




