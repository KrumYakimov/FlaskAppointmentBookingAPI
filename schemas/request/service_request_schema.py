from marshmallow import Schema, fields, validate


class ServiceBaseSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            "required": "Name is required.",
            "invalid": "Name must be a string.",
        },
    )
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        error_messages={
            "required": "Price is required.",
            "invalid": "Price must be a Numeric.",
        },
    )
    duration = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        error_messages={
            "required": "Duration is required.",
            "invalid": "Duration must be a Integer.",
        },
    )
    service_subcategory_id = fields.Integer(
        required=True,
        error_messages={
            "required": "Subcategory ID is required.",
            "invalid": "Subcategory ID must be an integer.",
        },
    )
    service_provider_id = fields.Integer(
        required=True,
        error_messages={
            "required": "Service Provider ID is required.",
            "invalid": "Service Provider ID must be an integer.",
        },
    )
    staff_id = fields.Integer(
        required=True,
        error_messages={
            "required": "Staff ID is required.",
            "invalid": "Staff ID must be an integer.",
        },
    )


class ServiceRequestSchema(ServiceBaseSchema):
    pass


class ServiceEditRequestSchema(ServiceBaseSchema):
    service_subcategory_id = fields.Int(required=False)
    service_provider_id = fields.Int(required=False)
    staff_id = fields.Int(required=False)
