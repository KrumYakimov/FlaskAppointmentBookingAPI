from marshmallow import Schema, fields


class CategoryResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    is_active = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    # TODO: Fetch the category name along with the subcategories' IDs and names.
