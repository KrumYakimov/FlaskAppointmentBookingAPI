from marshmallow import Schema, fields


class ServiceResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    subcategory_id = fields.Integer(dump_only=True)
    price = fields.Float(dump_only=True)
    duration_minutes = fields.Integer(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    # TODO: Fetch the subcategory name along with the categories' IDs and names.
    # TODO: Get all available services - list the different (distinct) values.


