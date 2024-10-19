from marshmallow import fields, validate, Schema

from utils.custom_validators import PersonalInfoValidator


class PersonalInfoSchema(Schema):
    email = PersonalInfoValidator.email()
    first_name = PersonalInfoValidator.first_name()
    last_name = PersonalInfoValidator.last_name()
    phone = PersonalInfoValidator.phone()


class TimestampSchema(Schema):
    created_on = fields.DateTime(dump_only=True)
    updated_on = fields.DateTime(dump_only=True)


class AddressSchema(Schema):
    country = fields.Str(
        required=True,
        validate=[
            validate.Length(equal=2, error="Country code must be exactly 2 characters."),
            validate.Regexp(
                r'^[A-Z]{2}$',
                error="Country code must consist of 2 uppercase letters."
            )
        ],
        error_messages={"required": "Country code is required."}
    )

    district = fields.Str(
        validate=validate.Length(min=2, max=50, error="District name must be between 2 and 50 characters.")
    )

    city = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50, error="City name must be between 2 and 50 characters."),
        error_messages={"required": "City is required."}
    )

    neighborhood = fields.Str(
        validate=validate.Length(min=2, max=50, error="Neighborhood name must be between 2 and 50 characters.")
    )

    street = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50, error="Street name must be between 2 and 50 characters."),
        error_messages={"required": "Street name is required."}
    )

    street_number = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^[0-9A-Za-z/-]+$',
            error="Street number must contain only alphanumeric characters, slashes, or hyphens."
        ),
        error_messages={"required": "Street number is required."}
    )

    block_number = fields.Str(
        validate=validate.Length(min=1, max=15, error="Block number must be between 1 and 15 characters.")
    )

    apartment = fields.Str(
        validate=validate.Length(min=1, max=15, error="Apartment number must be between 1 and 15 characters.")
    )

    floor = fields.Str(
        validate=validate.Length(min=1, max=255, error="Floor must be between 1 and 255 characters.")
    )

    postal_code = fields.Str(
        required=True,
        validate=[
            validate.Length(max=20, error="Postal code must be less than or equal to 20 characters."),
            validate.Regexp(
                r'^[A-Za-z0-9\s-]+$',
                error="Postal code must contain only alphanumeric characters, spaces, or hyphens."
            )
        ],
        error_messages={"required": "Postal code is required."}
    )

    latitude = fields.Float(
        validate=validate.Range(min=-90, max=90, error="Latitude must be between -90 and 90.")
    )

    longitude = fields.Float(
        validate=validate.Range(min=-180, max=180, error="Longitude must be between -180 and 180.")
    )
