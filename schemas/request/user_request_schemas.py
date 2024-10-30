from marshmallow import fields, validate, Schema, validates_schema, ValidationError

from schemas.mixins_schemas import PersonalInfoSchema
from utils.custom_validators import (
    PasswordValidator,
    PersonalInfoValidator,
    RoleValidator,
)


class ClientRegistrationRequestSchema(PersonalInfoSchema):
    password = fields.Str(
        required=True,
        validate=PasswordValidator().validate_password,
    )


class UserRegistrationRequestSchema(PersonalInfoSchema):
    password = fields.Str(
        required=True,
        validate=PasswordValidator().validate_password,
    )
    role = fields.Str(required=True, validate=RoleValidator().validate_role)
    service_provider_id = fields.Int(
        required=False
    )  # Make it optional, and validate based on role
    owned_company_ids = fields.List(fields.Int(), required=False)

    @validates_schema
    def validate_role_fields(self, data, **kwargs):
        """
        Validate that only the appropriate fields are provided based on the role.
        If both service_provider_id and owned_company_ids are provided, or if
        the required field for the role is missing, raise a validation error.
        """
        role = data.get("role")

        # Validate for STAFF
        if role == "STAFF":
            if "service_provider_id" not in data:
                raise ValidationError(
                    "Service Provider ID is required for staff.",
                    field_names=["service_provider_id"],
                )
            if "owned_company_ids" in data:
                raise ValidationError(
                    "Staff should not have associated owned companies.",
                    field_names=["owned_company_ids"],
                )

        # Validate for OWNER
        elif role == "OWNER":
            if "owned_company_ids" not in data:
                raise ValidationError(
                    "Owner must be associated with at least one service provider.",
                    field_names=["owned_company_ids"],
                )
            if "service_provider_id" in data:
                raise ValidationError(
                    "Owners should not be associated with a single Service Provider ID.",
                    field_names=["service_provider_id"],
                )

        # Validate for ADMIN or APPROVER
        if role in ["ADMIN", "APPROVER"]:
            if "service_provider_id" in data or "owned_company_ids" in data:
                raise ValidationError(
                    "Admins and Approvers should not be related to a Service Provider.",
                    field_names=["service_provider_id", "owned_company_ids"],
                )


class UserLoginRequestSchema(Schema):
    email = fields.Email(
        required=True,
        validate=validate.Email(error="Invalid email format."),
        error_messages={"required": "Email is required."},
    )
    password = fields.Str(required=True)


class PasswordChangeSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(
        required=True, validate=PasswordValidator().validate_password
    )

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data["old_password"] == data["new_password"]:
            raise ValidationError(
                "New password cannot be the same as the old password.",
                field_names=["new_password"],
            )


class UserEditRequestSchema(Schema):
    email = PersonalInfoValidator.email(required=False)
    first_name = PersonalInfoValidator.first_name(required=False)
    last_name = PersonalInfoValidator.last_name(required=False)
    phone = PersonalInfoValidator.phone(required=False)

    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        if not any(data.values()):
            raise ValidationError("At least one field must be provided for editing.")
