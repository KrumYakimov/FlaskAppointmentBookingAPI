from datetime import datetime, timedelta

import logging
import jwt
from decouple import config
from flask_httpauth import HTTPTokenAuth
from werkzeug.exceptions import Unauthorized

from db import db
from models.user import UserModel


class AuthManager:
    MISSING_TOKEN_MESSAGE = "Missing token!"
    TOKEN_EXPIRED_MESSAGE = "Token has expired!"
    INVALID_TOKEN_MESSAGE = "Invalid token!"
    TOKEN_DECODING_FAILED_MESSAGE = "Token decoding failed!"
    INVALID_OR_MISSING_TOKEN_MESSAGE = "Invalid or missing token!"

    @staticmethod
    def encode_token(user: UserModel) -> str:
        """
        Encodes the user's data into a JWT token.

        :param user: A UserModel object containing the 'id' and 'role' attributes.
        :return: A JWT token as a string.
        """
        payload = {
            "sub": user.id,
            "exp": datetime.utcnow() + timedelta(hours=int(config("TOKEN_EXPIRATION_HOURS"))),
            "role": user.role if isinstance(user.role, str) else user.role.name
        }
        token = jwt.encode(payload, key=config("SECRET_KEY"), algorithm="HS256")
        return token

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decodes a JWT token and returns the payload with 'sub' (user ID) and 'role'.

        :param token: JWT token as a string.
        :return: A dictionary containing the 'id' and 'role' from the token.
        :raises Unauthorized: If the token is missing or invalid.
        """
        if not token:
            raise Unauthorized(AuthManager.MISSING_TOKEN_MESSAGE)

        try:
            payload = jwt.decode(token, key=config("SECRET_KEY"), algorithms=["HS256"])
            return {"id": payload["sub"], "role": payload["role"]}
        except jwt.ExpiredSignatureError:
            raise Unauthorized(AuthManager.TOKEN_EXPIRED_MESSAGE)
        except jwt.InvalidTokenError:
            raise Unauthorized(AuthManager.INVALID_TOKEN_MESSAGE)
        except Exception as ex:
            logging.error(f"Token decoding failed: {str(ex)}")
            raise Unauthorized(AuthManager.TOKEN_DECODING_FAILED_MESSAGE)


auth = HTTPTokenAuth(scheme="Bearer")


@auth.verify_token
def verify_token(token: str) -> UserModel:
    """
    Verifies the provided JWT token by decoding it and fetching the corresponding user.

    :param token: JWT token as a string.
    :return: UserModel object if the token is valid and the user is found.
    :raises Unauthorized: If the token is invalid or the user does not exist.
    """
    try:
        decoded_token = AuthManager.decode_token(token)
        user_id = decoded_token["id"]
        user_role = decoded_token["role"]

        user = db.session.execute(db.select(UserModel).filter_by(id=user_id)).scalar()
        if user is None:
            raise Unauthorized(AuthManager.INVALID_OR_MISSING_TOKEN_MESSAGE)

        return user
    except Exception as ex:
        logging.error(f"Token verification failed: {str(ex)}")
        raise Unauthorized(AuthManager.INVALID_OR_MISSING_TOKEN_MESSAGE)
