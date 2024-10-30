from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, Conflict, Forbidden

from db import db
from models import ServiceProviderModel, InquiryModel, ProviderRegistrationState


class ProviderManager:
    @staticmethod
    def get_provider(status=None, provider_id=None):
        stmt = db.select(ServiceProviderModel).distinct()

        if provider_id:
            stmt = stmt.where(ServiceProviderModel.id == provider_id)

        if status:
            is_active = status.lower() == 'active'
            stmt = stmt.where(ServiceProviderModel.is_active == is_active)

        providers = db.session.execute(stmt).scalars().all()
        return providers

    @staticmethod
    def create_provider(data):
        inquiry_id = data.get("inquiry_id")

        inquiry = db.session.execute(
            db.select(InquiryModel).filter_by(id=inquiry_id)
        ).scalar_one_or_none()

        if not inquiry:
            raise NotFound(f"Inquiry with ID {inquiry_id} not found.")

        if inquiry.status != ProviderRegistrationState.APPROVED:
            raise Forbidden("Inquiry must be approved before registering a provider.")

        provider = ServiceProviderModel(**data)
        try:
            db.session.add(provider)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            raise Conflict("A provider with the provided data already exists.")

    @staticmethod
    def update_provider(provider_id, data):
        provider = db.session.execute(
            db.select(ServiceProviderModel).filter_by(id=provider_id)
        ).scalar_one_or_none()

        if not provider:
            raise NotFound(f"Service Provider with id {provider_id} not found.")

        for key, value in data.items():
            if hasattr(provider, key):
                setattr(provider, key, value)

        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            raise Conflict("Failed to update provider with the provided data.")

    @staticmethod
    def deactivate_provider(provider_id):
        provider = db.session.execute(
            db.select(ServiceProviderModel).filter_by(id=provider_id)
        ).scalar_one_or_none()

        if not provider:
            raise NotFound(f"User with id {provider_id} not found.")

        ProviderManager._deactivate_provider(provider)

    @staticmethod
    def _deactivate_provider(provider):
        provider.is_active = False

        db.session.add(provider)
        db.session.flush()

        # TODO: Implement logic so that when deactivating a provider,
        #  it also deactivates associated owners, employees, and services.



