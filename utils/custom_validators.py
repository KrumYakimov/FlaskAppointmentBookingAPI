from marshmallow import ValidationError
from marshmallow import fields, validate
from password_strength import PasswordPolicy, PasswordStats
from psycopg2.errors import UniqueViolation
from werkzeug.exceptions import Conflict

from utils.role_permitions import ROLE_PERMISSIONS


class PasswordValidator:
    pwd_policy = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1,
        special=1,
    )

    pwd_policy_error_mapper = {
        "length": "Your password needs to be at least 8 characters long.",
        "uppercase": "Your password should include at least one uppercase letter (A-Z).",
        "numbers": "Your password should contain at least one number (0-9).",
        "special": "Your password should include at least one special character (e.g., !, @, #, $, etc.).",
    }

    def validate_password(self, value):
        errors = self.pwd_policy.test(value)
        errors_messages = [self.pwd_policy_error_mapper[error.name()] for error in errors]

        password_strength = PasswordStats(value).strength()
        if password_strength < 0.2:
            errors_messages.append("Too common!")

        if errors_messages:
            raise ValidationError(errors_messages)


class UniqueConstraintValidator:
    def __init__(self, session):
        self.session = session

    """
    From a security point of view, it is generally better not to provide overly specific error messages 
    regarding the cause of failures like unique constraint violations. 
    Giving too much detail (such as whether an email or phone number is already registered) 
    can inadvertently expose information to malicious users, 
    such as confirming the existence of an account with a particular email or phone number.

    A more secure approach would be to provide a generic error message, preventing potential attackers 
    from gathering information about our user base, while still guiding legitimate users on how to proceed.
    """

    @staticmethod
    def check_unique_violation(error, email_key='inquiries_email_key', phone_key='inquiries_phone_key'):
        """Checks if the IntegrityError is due to a UniqueViolation and raises a generic Conflict error."""
        if isinstance(error.orig, UniqueViolation):
            # Log the specific error for internal use but give the user a generic message
            raise Conflict(
                "The provided information doesn't meet our data management policy. Please verify and try again.")

        # General fallback error message
        raise Conflict("An issue occurred during registration. Please try again later.")

    # def check_unique_violation(error, email_key='inquiries_email_key', phone_key='inquiries_phone_key'):
    #     """Checks if the IntegrityError is due to a UniqueViolation and raises appropriate Conflict."""
    #     if isinstance(error.orig, UniqueViolation):
    #         if email_key in str(error.orig):
    #             raise Conflict("This email is already in use.")
    #         elif phone_key in str(error.orig):
    #             raise Conflict("This phone number is already in use.")
    #     raise Conflict("There was a problem with the registration.")

    def rollback(self):
        """Rolls back the session in case of failure."""
        self.session.rollback()


class PersonalInfoValidator:
    @staticmethod
    def email(required=True):
        return fields.Email(
            required=required,
            validate=validate.Email(error="Invalid email format."),
            error_messages={"required": "Email is required." if required else None}
        )

    @staticmethod
    def first_name(required=True):
        return fields.Str(
            required=required,
            validate=[
                validate.Length(min=2, max=50, error="First name must be between 2 and 50 characters."),
                validate.Regexp(r'^[a-zA-Z]+$', error="First name must contain only letters.")
            ],
            error_messages={"required": "First name is required." if required else None}
        )

    @staticmethod
    def last_name(required=True):
        return fields.Str(
            required=required,
            validate=[
                validate.Length(min=2, max=50, error="Last name must be between 2 and 50 characters."),
                validate.Regexp(r'^[a-zA-Z]+$', error="Last name must contain only letters.")
            ],
            error_messages={"required": "Last name is required." if required else None}
        )

    @staticmethod
    def phone(required=True):
        return fields.Str(
            required=required,
            validate=validate.Regexp(
                r'^\d{10,15}$',
                error="Phone number must contain 10 to 15 digits."
            ),
            error_messages={"required": "Phone number is required." if required else None}
        )


class RoleValidator:
    @staticmethod
    def validate_role(value):
        value = value
        allowed_roles = set(ROLE_PERMISSIONS.keys()) | {
            role for permissions in ROLE_PERMISSIONS.values() for role_list in permissions.values() for role in role_list
        }

        # allowed_roles = set()
        # allowed_roles.update(ROLE_PERMISSIONS.keys())
        #
        # for permissions in ROLE_PERMISSIONS.values():
        #     for role_list in permissions.values():
        #         allowed_roles.update(role_list)

        if value not in allowed_roles:
            raise ValidationError(f"Invalid role '{value}'. Allowed roles are: {allowed_roles}")
