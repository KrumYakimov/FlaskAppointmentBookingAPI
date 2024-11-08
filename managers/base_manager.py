from typing import Optional, List, TypeVar, Generic, Dict, Any

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict

from db import db

ModelType = TypeVar('ModelType')


class BaseManager(Generic[ModelType]):
    model: Optional[ModelType] = None

    @classmethod
    def get_records(cls, status: Optional[str] = None, record_id: Optional[int] = None) -> List[model]:
        """
        Retrieves records from the specified model, optionally filtered by status and record ID.

        :param status: The status to filter records by (e.g., "active"). If None, all records are fetched.
        :param record_id: The specific record ID to retrieve. If None, all records are fetched.
        :return: A list of records matching the criteria.
        :raises NotImplementedError: If the model is not specified for the manager.
        :raises ValueError: If an invalid status is provided.
        """
        if not cls.model:
            raise NotImplementedError("Model not specified for the manager.")

        stmt = db.select(cls.model).distinct()

        if record_id:
            stmt = stmt.where(cls.model.id == record_id)

        if status is not None:
            is_active = status.lower() == "active"
            stmt = stmt.where(cls.model.is_active == is_active)

        records = db.session.execute(stmt).scalars().all()
        return records

    @classmethod
    def create(cls, data: Dict[str, Any]) -> ModelType:
        """
        Creates a new record in the database using the provided data
        :param data: A dictionary containing the data to create the record.
        :return: The newly created record.
        :raises Conflict: If a record with the provided data already exists.
        """
        item = cls.model(**data)
        try:
            db.session.add(item)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(
                f"A {cls.model.__name__} with the provided data already exists."
            )
        return item

    @classmethod
    def update(cls, item_id: int, data: Dict[str, Any]) -> None:
        """
        Updates an existing record in the database
        :param item_id: The ID of the record to update.
        :param data: A dictionary containing the updated data.
        :return: The updated record or None if not found.
        :raises Conflict: If the update fails due to integrity constraints.
        """
        item = cls.get_records(record_id=item_id, status="active")[0]
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(
                f"Failed to update {cls.model.__name__} with the provided data."
            )

    @classmethod
    def deactivate(cls, item_id: int) -> None:
        """
        Deactivates a record by setting its is_active attribute to False
        :param item_id: The ID of the record to deactivate.
        :return: The deactivated record or None if not found.
        """

        item = cls.get_records(record_id=item_id, status="active")[0]
        item.is_active = False
        db.session.add(item)
        db.session.flush()
