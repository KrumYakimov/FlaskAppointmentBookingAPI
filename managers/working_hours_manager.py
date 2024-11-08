from sqlite3 import IntegrityError
from typing import Optional, List, Dict, Any

from db import db
from managers.base_manager import BaseManager
from models.working_hours import WorkingHoursModel


class WorkingHoursManager(BaseManager):
    model = WorkingHoursModel

    @classmethod
    def get_working_hours(
        cls, provider_id: Optional[int] = None, staff_id: Optional[int] = None
    ) -> List[WorkingHoursModel]:
        """
        Retrieves working hours based on provider or staff ID.

        :param provider_id: The ID of the provider to filter working hours by (optional).
        :param staff_id: The ID of the staff member to filter working hours by (optional).
        :return: A list of WorkingHoursModel instances that match the criteria.
        """
        query = db.select(cls.model)
        if provider_id:
            query = query.where(cls.model.provider_id == provider_id)
        elif staff_id:
            query = query.where(cls.model.employee_id == staff_id)

        return db.session.execute(query).scalars().all()

    @classmethod
    def create_batch(
        cls, provider_id: int, employees_data: List[Dict[str, Any]]
    ) -> List[WorkingHoursModel]:
        """
        Creates multiple working hour entries for the specified provider.

        :param provider_id: The ID of the provider for whom to create working hours.
        :param employees_data: A list of dictionaries containing employee working hour details.
        :return: A list of created WorkingHoursModel instances.
        """
        entries = []
        for employee_data in employees_data:
            employee_id = employee_data["employee_id"]
            for hours in employee_data["working_hours"]:
                working_hour_data = {
                    "day_of_week": hours["day_of_week"],
                    "start_time": hours["start_time"],
                    "end_time": hours["end_time"],
                    "provider_id": provider_id,
                    "employee_id": employee_id,
                }
                try:
                    entry = cls.model(**working_hour_data)
                    db.session.add(entry)
                    db.session.flush()
                    entries.append(entry)
                except IntegrityError as e:
                    db.session.rollback()
        return entries

    # TODO: Batch editing
