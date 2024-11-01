from marshmallow import Schema, fields, validate, ValidationError


class WorkingHourBaseSchema(Schema):
    day_of_week = fields.Int(
        required=True,
        validate=validate.Range(min=0, max=6),
        error_messages={
            "required": "Day of the week is required.",
            "invalid": "Day of the week must be an integer between 0 (Monday) and 6 (Sunday).",
        },
    )
    start_time = fields.Time(required=True, error_messages={"required": "Start time is required."})
    end_time = fields.Time(required=True, error_messages={"required": "End time is required."})
    provider_id = fields.Int(required=True)
    employee_id = fields.Int(required=True)


class EmployeeWorkingHoursSchema(Schema):
    employee_id = fields.Int(required=True)
    working_hours = fields.List(fields.Nested(WorkingHourBaseSchema), required=True)


class WorkingHourBatchSchema(Schema):
    # Fields for single entry registration
    day_of_week = fields.Int(validate=validate.Range(min=0, max=6))
    start_time = fields.Time()
    end_time = fields.Time()
    provider_id = fields.Int()
    employee_id = fields.Int()

    # Required field for batch entries
    employees = fields.List(fields.Nested(EmployeeWorkingHoursSchema), required=False)

    @staticmethod
    def validate_required_fields(data):
        if "employees" in data:
            # Batch registration: Ensure `employees` is populated with working hours for each employee
            if not data["employees"]:
                raise ValidationError("Employees list cannot be empty for batch registration.")
        else:
            # Single entry registration: Ensure all fields are present
            required_fields = ["day_of_week", "start_time", "end_time", "provider_id", "employee_id"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields for single registration: {', '.join(missing_fields)}")


class WorkingHourEditRequestSchema(WorkingHourBaseSchema):
    provider_id = fields.Int(required=False)
    employee_id = fields.Int(required=False)
