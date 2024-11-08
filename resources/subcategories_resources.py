from typing import Optional

from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.subcategory_manager import SubCategoryManager
from models import RoleType
from schemas.request.subcategory_request_schema import (
    SubCategoryRequestSchema,
    SubCategoryEditRequestSchema,
)
from schemas.response.subcategory_response_schema import SubCategoryResponseSchema
from utils.decorators import validate_schema, permission_required


class SubCategoryProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(
        self, status: Optional[str] = None, subcategory_id: Optional[int] = None
    ) -> tuple:
        """
        Retrieves service subcategories based on the provided status and subcategory ID.

        :param status: Optional status to filter subcategories.
        :param subcategory_id: Optional ID of a specific subcategory to retrieve.
        :return: A tuple containing the serialized subcategory data and a 200 status code.
        """
        status = status or request.args.get("status", None)
        subcategory_id = subcategory_id or request.args.get("subcategory_id", None)
        subcategories = SubCategoryManager.get_records(
            status=status, record_id=subcategory_id
        )
        return SubCategoryResponseSchema().dump(subcategories, many=True), 200


class SubCategoryRegistration(Resource):
    @auth.login_required
    @validate_schema(SubCategoryRequestSchema)
    @permission_required(RoleType.APPROVER)
    def post(self) -> tuple:
        """
        Creates a new service subcategory.

        :return: A message indicating successful creation and a 201 status code.
        """
        data = request.get_json()
        SubCategoryManager.create(data)
        return {"message": "Service Subcategory created successfully"}, 201


class SubCategoryEditing(Resource):
    @auth.login_required
    @validate_schema(SubCategoryEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, subcategory_id: int) -> tuple:
        """
        Edits an existing service subcategory.

        :param subcategory_id: The ID of the subcategory to edit.
        :return: A message indicating successful update and a 200 status code.
        """
        data = request.get_json()
        SubCategoryManager.update(subcategory_id, data)
        return {"message": "Service Subcategory updated successfully"}, 200


class SubCategoryDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, subcategory_id: int) -> tuple:
        """
        Deactivates a service subcategory.

        :param subcategory_id: The ID of the subcategory to deactivate.
        :return: A message indicating successful deactivation and a 200 status code.
        """
        SubCategoryManager.deactivate(subcategory_id)
        return {"message": "Subcategory deactivated successfully."}, 200
