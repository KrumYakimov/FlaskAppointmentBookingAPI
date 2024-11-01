from sqlite3 import IntegrityError

from db import db
from managers.base_manager import BaseManager
from models.working_hours import WorkingHoursModel


class WorkingHoursManager(BaseManager):
    model = WorkingHoursModel

    @classmethod
    def get_working_hours(cls, provider_id=None, employee_id=None):
        query = db.select(cls.model)
        if provider_id:
            query = query.where(cls.model.provider_id == provider_id)
        elif employee_id:
            query = query.where(cls.model.employee_id == employee_id)

        return db.session.execute(query).scalars().all()

    @classmethod
    def create_batch(cls, provider_id, employees_data):
        entries = []
        for employee_data in employees_data:
            employee_id = employee_data["employee_id"]
            for hours in employee_data["working_hours"]:
                working_hour_data = {
                    "day_of_week": hours["day_of_week"],
                    "start_time": hours["start_time"],
                    "end_time": hours["end_time"],
                    "provider_id": provider_id,
                    "employee_id": employee_id
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

