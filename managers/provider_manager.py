
from db import db
from managers.base_manager import BaseManager
from models import ServiceProviderModel, InquiryModel, ProviderRegistrationState
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, Conflict, Forbidden


class ProviderManager(BaseManager):
    model = ServiceProviderModel

    @classmethod
    def get_provider(cls, status=None, provider_id=None):
        return cls.get_records(status=status, record_id=provider_id)

    @classmethod
    def create_provider(cls, data):
        inquiry_id = data.get("inquiry_id")
        inquiry = cls._get_inquiry(inquiry_id)

        if inquiry.status != ProviderRegistrationState.APPROVED:
            raise Forbidden("Inquiry must be approved before registering a provider.")

        try:
            provider = cls.create(data)
            return provider
        except IntegrityError:
            db.session.rollback()
            raise Conflict("A provider with the same UIC or Inquiry ID already exists.")

    @classmethod
    def update_provider(cls, provider_id, data):
        cls.update(provider_id, data)

    @classmethod
    def deactivate_provider(cls, provider_id):
        provider = cls.get_records(record_id=provider_id)[0]
        cls._deactivate_provider(provider)

    @staticmethod
    def _deactivate_provider(provider):
        provider.is_active = False
        db.session.add(provider)
        db.session.flush()
        # TODO: Implement additional logic to deactivate associated owners, employees, and services.

    @staticmethod
    def _get_inquiry(inquiry_id):
        inquiry = db.session.execute(
            db.select(InquiryModel).filter_by(id=inquiry_id)
        ).scalar_one_or_none()

        if not inquiry:
            raise NotFound(f"Inquiry with ID {inquiry_id} not found.")
        return inquiry
