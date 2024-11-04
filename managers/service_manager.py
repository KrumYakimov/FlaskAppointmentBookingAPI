from db import db
from managers.base_manager import BaseManager
from models import ServiceModel
from werkzeug.exceptions import NotFound


class ServiceManager(BaseManager):
    model = ServiceModel

    @staticmethod
    def get_service_duration(service_id):
        service = db.session.execute(
            db.select(ServiceModel).filter(ServiceModel.id == service_id)
        ).scalar_one_or_none()

        if service is None:
            raise NotFound(f"Service with ID {service_id} not found.")

        return (
            service.duration
        )
