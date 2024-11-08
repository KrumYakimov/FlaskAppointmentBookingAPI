from flask import request
from flask_restful import Resource

from managers.appointment_manager import AppointmentManager
from managers.auth_manager import auth
from managers.service_manager import ServiceManager
from models import RoleType
from schemas.request.appointment_request_schema import (
    CustomerAppointmentRequestSchema,
    CustomerAppointmentEditingRequestSchema,
)
from schemas.response.appointment_response_schema import (
    CustomerAppointmentResponseSchema,
)
from utils.decorators import validate_schema, permission_required


class AvailableSlots(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def get(self, staff_id: int, service_id: int, date: str) -> tuple:
        """
        Retrieves available time slots for a given staff member on a specified date.

        :param staff_id: The ID of the staff member.
        :param service_id: The ID of the service.
        :param date: The date in ISO format for which to retrieve available slots.
        :return: A tuple containing the available slots and a 200 status code.
        """
        service_duration = ServiceManager.get_service_duration(service_id)
        available_slots = AppointmentManager.get_available_slots(
            staff_id, service_duration, date
        )
        return {"available_slots": available_slots}, 200


class CustomerAppointments(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def get(self) -> tuple:
        """
        Retrieves all appointments for the logged-in client.

        :return: A tuple containing the appointment data and a 200 status code.
        """
        appointments = AppointmentManager.get_all()
        return CustomerAppointmentResponseSchema(many=True).dump(appointments), 200


class CustomerAppointmentBooking(Resource):
    @auth.login_required
    @validate_schema(CustomerAppointmentRequestSchema)
    @permission_required(RoleType.CLIENT)
    def post(self) -> tuple:
        """
        Books a new appointment for the logged-in client.

        :return: A tuple containing the created appointment data and a 201 status code.
        """
        data = request.get_json()
        current_user = auth.current_user()
        created_appointment = AppointmentManager.create(data, current_user)
        return CustomerAppointmentResponseSchema().dump(created_appointment), 201


class CustomerAppointmentEditing(Resource):
    @auth.login_required
    @validate_schema(CustomerAppointmentEditingRequestSchema)
    @permission_required(RoleType.CLIENT)
    def put(self, appointment_id: int) -> tuple:
        """
        Edits an existing appointment for the logged-in client.

        :param appointment_id: The ID of the appointment to edit.
        :return: A tuple with a success message and a 200 status code.
        """
        data = request.get_json()
        current_user = auth.current_user()
        AppointmentManager.update(appointment_id, data, current_user)
        return {"message": "Appointment updated successfully"}, 200


class CustomerAppointmentCancellation(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def delete(self, appointment_id: int) -> tuple:
        """
        Cancels an existing appointment for the logged-in client.

        :param appointment_id: The ID of the appointment to cancel.
        :return: A tuple with an empty body and a 204 status code.
        """
        AppointmentManager.delete(appointment_id)
        return "", 204


class StaffAppointmentConfirmation(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id: int) -> tuple:
        """
        Confirms an existing appointment for the logged-in staff member.

        :param appointment_id: The ID of the appointment to confirm.
        :return: A tuple with a success message and a 200 status code.
        """
        current_user = auth.current_user()
        AppointmentManager.confirm_appointment(appointment_id, current_user)
        return {"message": "Appointment confirmed successfully"}, 200


class StaffAppointmentRejection(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id: int) -> tuple:
        """
        Rejects an existing appointment for the logged-in staff member.

        :param appointment_id: The ID of the appointment to reject.
        :return: A tuple with a success message and a 200 status code.
        """
        current_user = auth.current_user()
        AppointmentManager.reject_appointment(appointment_id, current_user)
        return {"message": "Appointment rejected successfully"}, 200


class StaffAppointmentCancellation(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id: int) -> tuple:
        """
        Cancels an existing appointment for the logged-in staff member.

        :param appointment_id: The ID of the appointment to cancel.
        :return: A tuple with a success message and a 200 status code.
        """
        current_user = auth.current_user()
        AppointmentManager.cancel_appointment(appointment_id, current_user)
        return {"message": "Appointment canceled successfully"}, 200


class StaffAppointmentNoShow(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id: int) -> tuple:
        """
        Marks an appointment as a no-show for the logged-in staff member.

        :param appointment_id: The ID of the appointment to mark as no-show.
        :return: A tuple with a success message and a 200 status code.
        """
        current_user = auth.current_user()
        AppointmentManager.no_show_inquiry(appointment_id, current_user)
        return {"message": "Appointment no showed successfully"}, 200


class StaffAppointmentCompletion(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id: int) -> tuple:
        """
        Marks an appointment as completed for the logged-in staff member.

        :param appointment_id: The ID of the appointment to mark as completed.
        :return: A tuple with a success message and a 200 status code.
        """
        current_user = auth.current_user()
        AppointmentManager.complete_appointment(appointment_id, current_user)
        return {"message": "Appointment completed successfully"}, 200
