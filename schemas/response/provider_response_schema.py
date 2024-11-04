from marshmallow import Schema, fields

from schemas.response.user_response_schemas import UserResponseSchema


class ProviderResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    is_active = fields.Str(dump_only=True)
    company_name = fields.Str(dump_only=True)
    trade_name = fields.Str(dump_only=True)
    uic = fields.Str(dump_only=True)
    photo_url = fields.URL(required=True)
    created_on = fields.DateTime(dump_only=True)
    inquiry_id = fields.Int(dump_only=True)
    employees = fields.List(fields.Nested(UserResponseSchema), dump_only=True)
    owners = fields.List(fields.Nested(UserResponseSchema), dump_only=True)

    # TODO: Extend the fields.
    # services = fields.List(fields.Nested("ServiceResponseSchema"), dump_only=True)
