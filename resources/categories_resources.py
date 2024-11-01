from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.category_manager import CategoryManager
from models import RoleType
from schemas.request.category_request_schema import CategoryRequestSchema, CategoryEditRequestSchema
from schemas.response.category_response_schema import CategoryResponseSchema
from utils.decorators import validate_schema, permission_required


class CategoryProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(self, status=None, category_id=None):
        status = status or request.args.get("status", None)
        category_number = category_id or request.args.get("category_number", None)
        categories = CategoryManager.get_records(status=status, record_id=category_id)
        return CategoryResponseSchema().dump(categories, many=True), 200


class CategoryRegistration(Resource):
    @auth.login_required
    @validate_schema(CategoryRequestSchema)
    @permission_required(RoleType.APPROVER)
    def post(self):
        data = request.get_json()
        CategoryManager.create(data)
        return {"message": "Service Category created successfully"}, 201


class CategoryEditing(Resource):
    @auth.login_required
    @validate_schema(CategoryEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, category_id):
        data = request.get_json()
        CategoryManager.update(category_id, data)
        return {"message": "Service Category updated successfully"}, 200


class CategoryDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, category_id):
        CategoryManager.deactivate(category_id)
        return {"message": "Category deactivated successfully."}, 200

