from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.provider_manager import ProviderManager
from models import RoleType
from schemas.request.provider_request_schema import (
    ProviderRegistrationRequestSchema,
    ProviderEditRequestSchema,
)
from schemas.response.provider_response_schema import ProviderResponseSchema
from utils.decorators import (
    permission_required,
    validate_schema,
)


class ProviderProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(self, status: str = None, provider_id: int = None) -> tuple:
        """
        Retrieves service providers based on the provided status and provider ID.

        :param status: Optional status to filter providers.
        :param provider_id: Optional ID of a specific provider to retrieve.
        :return: A tuple containing the serialized provider data and a 200 status code.
        """
        status = status or request.args.get("status", None)
        provider_number = provider_id or request.args.get("provider_number", None)
        providers = ProviderManager.get_records(status=status, record_id=provider_id)
        return {"providers": ProviderResponseSchema().dump(providers, many=True)}, 200


class ProviderRegistration(Resource):
    @auth.login_required
    @validate_schema(ProviderRegistrationRequestSchema)
    @permission_required(RoleType.APPROVER)
    def post(self) -> tuple:
        """
        Creates a new service provider.

        :return: A message indicating successful creation and a 201 status code.
        """
        data = request.get_json()
        ProviderManager.create_provider(data)
        return {"message": "Service Provider created successfully"}, 201


class ProviderEditing(Resource):
    @auth.login_required
    @validate_schema(ProviderEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, provider_id: int) -> tuple:
        """
        Edits an existing service provider.

        :param provider_id: The ID of the provider to edit.
        :return: A message indicating successful update and a 200 status code.
        """
        data = request.get_json()
        ProviderManager.update(provider_id, data)
        return {"message": "Service Provider updated successfully"}, 200


class ProviderDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, provider_id: int) -> tuple:
        """
        Deactivates a service provider.

        :param provider_id: The ID of the provider to deactivate.
        :return: A message indicating successful deactivation and a 200 status code.
        """
        ProviderManager.deactivate_provider(provider_id)
        return {"message": "Account deactivated successfully."}, 200
