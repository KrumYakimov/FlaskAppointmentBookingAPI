# base_manager.py
from db import db
from werkzeug.exceptions import NotFound, Conflict
from sqlalchemy.exc import IntegrityError


class BaseManager:
    model = None

    @classmethod
    def get_records(cls, status=None, record_id=None):
        """
        Generic method to retrieve records with optional status and ID filters.
        """
        if not cls.model:
            raise NotImplementedError("Model not specified for the manager.")

        stmt = db.select(cls.model).distinct()

        if record_id:
            stmt = stmt.where(cls.model.id == record_id)

        if status is not None:
            is_active = status.lower() == 'active'
            stmt = stmt.where(cls.model.is_active == is_active)

        records = db.session.execute(stmt).scalars().all()
        return records

    @classmethod
    def create(cls, data):
        item = cls.model(**data)
        try:
            db.session.add(item)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(f"A {cls.model.__name__} with the provided data already exists.")
        return item

    @classmethod
    def update(cls, item_id, data):
        item = cls.get_records(record_id=item_id, status="active")[0]
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(f"Failed to update {cls.model.__name__} with the provided data.")

    @classmethod
    def deactivate(cls, item_id):
        item = cls.get_records(record_id=item_id, status="active")[0]
        item.is_active = False
        db.session.add(item)
        db.session.flush()
