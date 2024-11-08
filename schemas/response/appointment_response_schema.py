from marshmallow import Schema, fields


class CustomerAppointmentResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    service_id = fields.Int(dump_only=True)
    staff_id = fields.Int(dump_only=True)
    appointment_time = fields.DateTime(dump_only=True)
    status = fields.String(dump_only=True)
