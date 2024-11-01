from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.subcategory_manager import SubCategoryManager
from models import RoleType, ServiceSubcategoryModel
from schemas.request.subcategory_request_schema import SubCategoryRequestSchema, SubCategoryEditRequestSchema
from schemas.response.subcategory_response_schema import SubCategoryResponseSchema
from utils.decorators import validate_schema, permission_required


class SubCategoryProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(self, status=None, subcategory_id=None):
        status = status or request.args.get("status", None)
        subcategory_id = subcategory_id or request.args.get("subcategory_id", None)
        subcategories = SubCategoryManager.get_records(status=status, record_id=subcategory_id)
        return SubCategoryResponseSchema().dump(subcategories, many=True), 200


class SubCategoryRegistration(Resource):
    @auth.login_required
    @validate_schema(SubCategoryRequestSchema)
    @permission_required(RoleType.APPROVER)
    def post(self):
        data = request.get_json()
        SubCategoryManager.create(data)
        return {"message": "Service Subcategory created successfully"}, 201


class SubCategoryEditing(Resource):
    @auth.login_required
    @validate_schema(SubCategoryEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, subcategory_id):
        data = request.get_json()
        SubCategoryManager.update(subcategory_id, data)
        return {"message": "Service Subcategory updated successfully"}, 200


class SubCategoryDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, subcategory_id):
        SubCategoryManager.deactivate(subcategory_id)
        return {"message": "Subcategory deactivated successfully."}, 200
