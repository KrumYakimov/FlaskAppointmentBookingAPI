from marshmallow import fields, validate, validates_schema, ValidationError

from schemas.mixins_schemas import AddressSchema
from utils.decorators import make_optional


class ProviderRegistrationRequestSchema(AddressSchema):
    company_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "Company name is required."},
    )

    trade_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "Trade name is required."},
    )

    uic = fields.Str(
        required=True,
        validate=[
            validate.Length(min=9, max=20, error="UIC must be exactly 20 characters."),
            validate.Regexp(
                r"^[A-Za-z0-9]+$",
                error="UIC must contain only alphanumeric characters.",
            ),
        ],
        error_messages={"required": "UIC is required."},
    )

    photo = fields.String(required=True)
    photo_extension = fields.String(required=True)

    inquiry_id = fields.Int(
        required=True,
        error_messages={
            "required": "Inquiry ID is required.",
            "invalid": "Inquiry ID must be an integer.",
        },
    )


@make_optional
class ProviderEditRequestSchema(AddressSchema):
    company_name = fields.Str(
        required=False,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "Company name is required."},
    )

    trade_name = fields.Str(
        required=False,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "Trade name is required."},
    )

    @validates_schema
    def validate_at_least_one_field(self, data: dict, **kwargs) -> None:
        if not any(data.values()):
            raise ValidationError("At least one field must be provided for editing.")
