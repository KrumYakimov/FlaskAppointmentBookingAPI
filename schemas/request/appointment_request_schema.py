from marshmallow import Schema, fields, validate, ValidationError, validates
from datetime import datetime

from managers.working_hours_manager import WorkingHoursManager


# class AvailableSlotsRequestSchema(Schema):
#     service_id = fields.Int(
#         required=True,
#         error_messages={
#             "required": "Service ID is required.",
#             "invalid": "Service ID must be an integer."
#         }
#     )
#     staff_id = fields.Int(
#         required=True,
#         error_messages={
#             "required": "Staff ID is required.",
#             "invalid": "Staff ID must be an integer."
#         }
#     )
#     date = fields.DateTime(
#         required=True,
#         format="%Y-%m-%dT%H:%M:%S",
#         error_messages={
#             "required": "Date is required.",
#             "invalid": "Date must be a valid datetime in ISO format."
#         }
#     )
#
#     @validates('date')
#     def validate_date(self, date):
#         """Custom validation to ensure the date is in the future."""
#         if date < datetime.now():
#             raise ValidationError("The date must be in the future.")


class AppointmentBaseSchema(Schema):
    service_id = fields.Int(
        required=True,
        error_messages={
            "required": "Service ID is required.",
            "invalid": "Service ID must be an integer.",
        },
    )
    staff_id = fields.Int(
        required=True,
        error_messages={
            "required": "Staff ID is required.",
            "invalid": "Staff ID must be an integer.",
        },
    )
    appointment_time = fields.DateTime(
        required=True,
        error_messages={
            "required": "Appointment time is required.",
            "invalid": "Appointment time must be a valid datetime.",
        },
    )

    # @validates("appointment_time")
    # def validate_appointment_time_field(self, appointment_time):
    #     """Validate that the appointment time is in the future."""
    #     if appointment_time < datetime.now():
    #         raise ValidationError("Appointment time must be in the future.")

    @validates('appointment_time')
    def validate_appointment_time(self, appointment_time):
        if appointment_time < datetime.now():
            raise ValidationError("Appointment time must be in the future.")

        staff_id = self.context.get('staff_id')
        working_hours = WorkingHoursManager.get_working_hours(staff_id)

        if not working_hours:
            raise ValidationError("This staff member has no working hours defined.")

        valid = False
        for hours in working_hours:
            start_time = datetime.combine(appointment_time.date(), hours.start_time)
            end_time = datetime.combine(appointment_time.date(), hours.end_time)
            if start_time <= appointment_time <= end_time:
                valid = True
                break
        if not valid:
            raise ValidationError("Appointment time is outside of working hours.")


class CustomerAppointmentRequestSchema(AppointmentBaseSchema):
    pass


class CustomerAppointmentEditingRequestSchema(AppointmentBaseSchema):
    service_id = fields.Int(required=False)
    staff_id = fields.Int(required=False)
