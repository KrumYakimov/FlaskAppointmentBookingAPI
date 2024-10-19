from marshmallow import fields, validate

from schemas.mixins_schemas import PersonalInfoSchema


class InquiryRegistrationRequestSchema(PersonalInfoSchema):
    salon_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50, error="Salon name must be between 2 and 50 characters."),
        error_messages={"required": "Salon name is required."}
    )

    city = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50, error="City name must be between 2 and 50 characters."),
        error_messages={"required": "City is required."}
    )