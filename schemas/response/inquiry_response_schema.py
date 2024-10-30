from marshmallow import Schema, fields


class InquiryResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    status = fields.Str(dump_only=True)
    salon_name = fields.Str(dump_only=True)
    city = fields.Str(dump_only=True)
    first_name = fields.Str(dump_only=True)
    last_name = fields.Str(dump_only=True)
    phone = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    created_on = fields.DateTime(dump_only=True)
