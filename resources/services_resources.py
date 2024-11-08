from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.service_manager import ServiceManager
from models import RoleType
from schemas.request.service_request_schema import (
    ServiceRequestSchema,
    ServiceEditRequestSchema,
)
from schemas.response.service_response_schema import ServiceResponseSchema
from utils.decorators import validate_schema, permission_required


class ServiceProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(self, status: str = None, service_id: int = None) -> tuple:
        """
        Retrieves service profiles based on the provided status and service ID.

        :param status: Optional status to filter services.
        :param service_id: Optional ID of a specific service to retrieve.
        :return: A tuple containing the serialized service data and a 200 status code.
        """
        status = status or request.args.get("status", None)
        service_id = service_id or request.args.get("service_id", None)
        services = ServiceManager.get_records(status=status, record_id=service_id)
        return ServiceResponseSchema().dump(services, many=True), 200


class ServiceRegistration(Resource):
    @auth.login_required
    @validate_schema(ServiceRequestSchema)
    @permission_required(RoleType.APPROVER)
    def post(self) -> tuple:
        """
        Creates a new service.

        :return: A message indicating successful creation and a 201 status code.
        """
        data = request.get_json()
        ServiceManager.create(data)
        return {"message": "Service created successfully"}, 201


class ServiceEditing(Resource):
    @auth.login_required
    @validate_schema(ServiceEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, service_id: int) -> tuple:
        """
        Edits an existing service.

        :param service_id: The ID of the service to edit.
        :return: A message indicating successful update and a 200 status code.
        """
        data = request.get_json()
        ServiceManager.update(service_id, data)
        return {"message": "Service updated successfully"}, 200


class ServiceDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, service_id: int) -> tuple:
        """
        Deactivates a service.

        :param service_id: The ID of the service to deactivate.
        :return: A message indicating successful deactivation and a 200 status code.
        """
        ServiceManager.deactivate(service_id)
        return {"message": "Service deactivated successfully."}, 200
