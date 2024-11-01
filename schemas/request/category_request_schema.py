from marshmallow import Schema, fields
from marshmallow import fields, validate


class CategoryBaseSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={"required": "Name is required.", "invalid": "Name must be a string."}
    )


class CategoryRequestSchema(CategoryBaseSchema):
    pass


class CategoryEditRequestSchema(CategoryBaseSchema):
    pass
