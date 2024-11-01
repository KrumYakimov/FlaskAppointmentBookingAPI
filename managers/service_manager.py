from managers.base_manager import BaseManager
from models import ServiceModel


class ServiceManager(BaseManager):
    model = ServiceModel
