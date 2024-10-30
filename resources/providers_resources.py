from flask_restful import Resource
from flask import request

from managers.auth_manager import auth
from managers.provider_manager import ProviderManager
from models import RoleType
from schemas.request.provider_request_schema import ProviderRegistrationRequestSchema, ProviderEditRequestSchema
from schemas.response.provider_response_schema import ProviderResponseSchema
from utils.decorators import role_based_access_control, permission_required, validate_schema


class ProviderProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(self, status=None, provider_id=None):
        status = status or request.args.get('status', None)
        provider_number = provider_id or request.args.get('provider_number', None)
        providers = ProviderManager.get_provider(status=status, provider_id=provider_id)
        return {"providers": ProviderResponseSchema().dump(providers, many=True)}, 200


class ProviderRegistration(Resource):
    @auth.login_required
    @validate_schema(ProviderRegistrationRequestSchema)
    @permission_required(RoleType.APPROVER)
    def post(self):
        data = request.get_json()
        ProviderManager.create_provider(data)
        return {"message": "Service Provider created successfully"}, 201


class ProviderEditing(Resource):
    @auth.login_required
    @validate_schema(ProviderEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, provider_id):
        data = request.get_json()
        ProviderManager.update_provider(provider_id, data)
        return {"message": "Service Provider updated successfully"}, 200


class ProviderDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, provider_id):
        ProviderManager.deactivate_provider(provider_id)
        return {"message": "Account deactivated successfully."}, 200
