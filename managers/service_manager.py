from typing import Optional

from werkzeug.exceptions import NotFound

from db import db
from managers.base_manager import BaseManager
from models import ServiceModel


class ServiceManager(BaseManager):
    model = ServiceModel

    @staticmethod
    def get_service_duration(service_id: int) -> Optional[int]:
        """
        Retrieves the duration of a service based on the provided service ID.

        :param service_id: The ID of the service for which to retrieve the duration.
        :return: The duration of the service in minutes.
        :raises NotFound: If the service with the given ID does not exist.
        """
        service = db.session.execute(
            db.select(ServiceModel).filter(ServiceModel.id == service_id)
        ).scalar_one_or_none()

        if service is None:
            raise NotFound(f"Service with ID {service_id} not found.")

        return (
            service.duration
        )
