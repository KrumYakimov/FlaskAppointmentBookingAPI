from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.service_manager import ServiceManager
from models import RoleType
from schemas.request.service_request_schema import ServiceRequestSchema, ServiceEditRequestSchema
from schemas.response.service_response_schema import ServiceResponseSchema
from utils.decorators import validate_schema, permission_required


class ServiceProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(self, status=None, service_id=None):
        status = status or request.args.get("status", None)
        service_id = service_id or request.args.get("service_id", None)
        services = ServiceManager.get_records(status=status, record_id=service_id)
        return ServiceResponseSchema().dump(services, many=True), 200


class ServiceRegistration(Resource):
    @auth.login_required
    @validate_schema(ServiceRequestSchema)
    @permission_required(RoleType.APPROVER)
    def post(self):
        data = request.get_json()
        ServiceManager.create(data)
        return {"message": "Service created successfully"}, 201


class ServiceEditing(Resource):
    @auth.login_required
    @validate_schema(ServiceEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, service_id):
        data = request.get_json()
        ServiceManager.update(service_id, data)
        return {"message": "Service updated successfully"}, 200


class ServiceDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, service_id):
        ServiceManager.deactivate(service_id)
        return {"message": "Service deactivated successfully."}, 200
