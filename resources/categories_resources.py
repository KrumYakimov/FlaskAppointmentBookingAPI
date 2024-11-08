from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.category_manager import CategoryManager
from models import RoleType
from schemas.request.category_request_schema import (
    CategoryRequestSchema,
    CategoryEditRequestSchema,
)
from schemas.response.category_response_schema import CategoryResponseSchema
from utils.decorators import validate_schema, permission_required


class CategoryProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(self, status: str = None, category_id: int = None) -> tuple:
        """
        Retrieves service categories based on the provided status and category ID.

        :param status: Optional status to filter categories.
        :param category_id: Optional ID of a specific category to retrieve.
        :return: A tuple containing the serialized category data and a 200 status code.
        """
        status = status or request.args.get("status", None)
        category_number = category_id or request.args.get("category_number", None)
        categories = CategoryManager.get_records(status=status, record_id=category_id)
        return CategoryResponseSchema().dump(categories, many=True), 200


class CategoryRegistration(Resource):
    @auth.login_required
    @validate_schema(CategoryRequestSchema)
    @permission_required(RoleType.APPROVER)
    def post(self) -> tuple:
        """
        Creates a new service category.

        :return: A message indicating successful creation and a 201 status code.
        """
        data = request.get_json()
        CategoryManager.create(data)
        return {"message": "Service Category created successfully"}, 201


class CategoryEditing(Resource):
    @auth.login_required
    @validate_schema(CategoryEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, category_id: int) -> tuple:
        """
        Edits an existing service category.

        :param category_id: The ID of the category to edit.
        :return: A message indicating successful update and a 200 status code.
        """
        data = request.get_json()
        CategoryManager.update(category_id, data)
        return {"message": "Service Category updated successfully"}, 200


class CategoryDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, category_id: int) -> tuple:
        """
        Deactivates a service category.

        :param category_id: The ID of the category to deactivate.
        :return: A message indicating successful deactivation and a 200 status code.
        """
        CategoryManager.deactivate(category_id)
        return {"message": "Category deactivated successfully."}, 200
