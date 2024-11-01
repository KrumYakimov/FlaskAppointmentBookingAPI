from marshmallow import Schema, fields


class SubCategoryResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    category_id = fields.Int(dump_only=True)
    is_active = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    # TODO: Fetch the name of the subcategory along with the category's ID and name.
