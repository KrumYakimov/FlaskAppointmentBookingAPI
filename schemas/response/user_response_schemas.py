from marshmallow import Schema, fields


class ClientResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(dump_only=True)
    last_name = fields.Str(dump_only=True)
    phone = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    created_on = fields.DateTime(dump_only=True)


class UserResponseSchema(ClientResponseSchema):
    role = fields.Str(dump_only=True)
    service_provider_id = fields.Int(dump_only=True)
    is_active = fields.Str(dump_only=True)
    password = fields.Str(load_only=True)

