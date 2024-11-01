from marshmallow import Schema, fields
from marshmallow import fields, validate


class SubCategoryBaseSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={
            "required": "Name is required.",
            "invalid": "Name must be a string."
        }
    )
    category_id = fields.Int(
        required=True,
        error_messages={
            "required": "Category ID is required.",
            "invalid": "Category ID must be an integer."
        }
    )


class SubCategoryRequestSchema(SubCategoryBaseSchema):
    pass


class SubCategoryEditRequestSchema(SubCategoryBaseSchema):
    category_id = fields.Int(required=False)
