from managers.base_manager import BaseManager
from models import ServiceCategoryModel


class CategoryManager(BaseManager):
    model = ServiceCategoryModel
