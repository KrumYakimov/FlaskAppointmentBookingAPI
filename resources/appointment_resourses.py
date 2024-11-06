from datetime import datetime

from flask import request
from flask_restful import Resource

from managers.appointment_manager import AppointmentManager
from managers.auth_manager import auth
from managers.service_manager import ServiceManager
from models import RoleType
from schemas.request.appointment_request_schema import CustomerAppointmentRequestSchema, \
    CustomerAppointmentEditingRequestSchema
from schemas.response.appointment_response_schema import CustomerAppointmentResponseSchema
from utils.decorators import validate_schema, permission_required


class AvailableSlots(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def get(self, staff_id, service_id, date):
        service_duration = ServiceManager.get_service_duration(service_id)
        available_slots = AppointmentManager.get_available_slots(staff_id, service_duration, date)
        return {"available_slots": available_slots}, 200


class CustomerAppointments(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def get(self):
        appointments = AppointmentManager.get_all()
        return CustomerAppointmentResponseSchema(many=True).dump(appointments), 200


class CustomerAppointmentBooking(Resource):
    @auth.login_required
    @validate_schema(CustomerAppointmentRequestSchema)
    @permission_required(RoleType.CLIENT)
    def post(self):
        data = request.get_json()
        current_user = auth.current_user()
        created_appointment = AppointmentManager.create(data, current_user)
        return CustomerAppointmentResponseSchema().dump(created_appointment), 201


class CustomerAppointmentEditing(Resource):
    @auth.login_required
    @validate_schema(CustomerAppointmentEditingRequestSchema)
    @permission_required(RoleType.CLIENT)
    def put(self, appointment_id):
        data = request.get_json()
        current_user = auth.current_user()
        AppointmentManager.update(appointment_id, data, current_user)
        return {"message": "Appointment updated successfully"}, 200


class CustomerAppointmentCancellation(Resource):
    @auth.login_required
    @permission_required(RoleType.CLIENT)
    def delete(self, appointment_id):
        AppointmentManager.delete(appointment_id)
        return {"message": "Appointment deleted successfully"}, 200


class StaffAppointmentConfirmation(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id):
        current_user = auth.current_user()
        AppointmentManager.confirm_appointment(appointment_id, current_user)
        return {"message": "Appointment confirmed successfully"}, 200


class StaffAppointmentRejection(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id):
        current_user = auth.current_user()
        AppointmentManager.reject_appointment(appointment_id, current_user)
        return {"message": "Appointment rejected successfully"}, 200


class StaffAppointmentCancellation(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id):
        current_user = auth.current_user()
        AppointmentManager.cancel_appointment(appointment_id, current_user)
        return {"message": "Inquiry canceled successfully"}, 200


class StaffAppointmentNoShow(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id):
        current_user = auth.current_user()
        AppointmentManager.no_show_inquiry(appointment_id, current_user)
        return {"message": "Inquiry no showed successfully"}, 200


class StaffAppointmentCompletion(Resource):
    @auth.login_required
    @permission_required(RoleType.STAFF)
    def put(self, appointment_id):
        current_user = auth.current_user()
        AppointmentManager.complete_appointment(appointment_id, current_user)
        return {"message": "Inquiry completed successfully"}, 200

