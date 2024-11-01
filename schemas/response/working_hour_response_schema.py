from marshmallow import Schema, fields


class WorkingHourResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    day_of_week = fields.Int(dump_only=True)
    start_time = fields.Time(dump_only=True)
    end_time = fields.Time(dump_only=True)
    provider_id = fields.Int(dump_only=True)
    employee_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
