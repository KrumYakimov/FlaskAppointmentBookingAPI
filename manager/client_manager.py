from werkzeug.exceptions import BadRequest, Unauthorized
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from manager.auth_manager import AuthManager
from models import UserModel
from models.emums import RoleType


class ClientManager:
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
        client = UserModel(**client_data)
        try:
            db.session.add(client)
            db.session.flush()
            return AuthManager.encode_token(client)
        except Exception as ex:
            raise BadRequest(f"Error during registration: {str(ex)}")

    @staticmethod
    def login(data: dict) -> str:
        """
        Checks the email and password (hashes the plain password)

        :param data: dict containing 'email' and 'password'.
        :return: A JWT token as a string for the logged-in user.
        :raises Unauthorized: If the email or password is incorrect.
        """

        user = db.session.execute(db.select(UserModel).filter_by(email=data["email"])).scalar()
        if not user or not check_password_hash(user.password, data["password"]):
            raise Unauthorized(ClientManager.INVALID_USERNAME_OR_PASSWORD_MESSAGE)
        return AuthManager.encode_token(user)
