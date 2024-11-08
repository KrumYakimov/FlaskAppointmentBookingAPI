from typing import Optional

from flask import request
from flask_restful import Resource

from managers.auth_manager import auth
from managers.working_hours_manager import WorkingHoursManager
from models import RoleType
from schemas.request.working_hour_request_schema import (
    WorkingHourEditRequestSchema,
    WorkingHourBatchSchema,
)
from schemas.response.working_hour_response_schema import WorkingHourResponseSchema
from utils.decorators import validate_schema, permission_required


class WorkingHourProfile(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(
        self, provider_id: Optional[int] = None, employee_id: Optional[int] = None
    ) -> tuple:
        """
        Retrieves working hours for a specified provider or employee.

        :param provider_id: Optional ID of the provider.
        :param employee_id: Optional ID of the employee.
        :return: A tuple containing the serialized working hour data and a 200 status code.
        """
        provider_id = provider_id or request.args.get("provider_id")
        employee_id = employee_id or request.args.get("employee_id")

        working_hours = WorkingHoursManager.get_working_hours(
            provider_id=provider_id, employee_id=employee_id
        )
        return WorkingHourResponseSchema().dump(working_hours, many=True), 200

    # TODO: Fetch info by working_hour_id


class WorkingHourRegistration(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    @validate_schema(WorkingHourBatchSchema)
    def post(self) -> tuple:
        """
        Registers new working hours, either in batch or single.

        :return: A message indicating successful creation and a 201 status code.
        """
        data = request.get_json()

        provider_id = data["provider_id"]

        if "employees" in data:
            # Batch registration
            created_entries = WorkingHoursManager.create_batch(
                provider_id, data["employees"]
            )
            return {
                "message": "Batch working hours created successfully",
                "working_hour_ids": [entry.id for entry in created_entries],
            }, 201
        else:
            # Single registration
            created_entry = WorkingHoursManager.create(data)
            return {
                "message": "Working hour created successfully",
                "working_hour_id": created_entry.id,
            }, 201


class WorkingHourEditing(Resource):
    @auth.login_required
    @validate_schema(WorkingHourEditRequestSchema)
    @permission_required(RoleType.APPROVER)
    def put(self, working_hours_id: int) -> tuple:
        """
        Edits existing working hours.

        :param working_hours_id: The ID of the working hours to edit.
        :return: A message indicating successful update and a 200 status code.
        """
        data = request.get_json()
        WorkingHoursManager.update(working_hours_id, data)
        return {"message": "Working hours updated successfully"}, 200

    # TODO: Batch editing


class WorkingHourDeactivate(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, working_hours_id: int) -> tuple:
        """
        Deactivates specified working hours.

        :param working_hours_id: The ID of the working hours to deactivate.
        :return: A message indicating successful deactivation and a 200 status code.
        """
        WorkingHoursManager.deactivate(working_hours_id)
        return {"message": "Working hours deactivated successfully"}, 200
