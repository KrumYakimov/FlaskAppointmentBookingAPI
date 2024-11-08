import os
import uuid
from typing import Optional, List

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, Conflict, Forbidden

from constants import TEMP_FILE_FOLDER
from db import db
from managers.base_manager import BaseManager
from models import ServiceProviderModel, InquiryModel, ProviderRegistrationState
from services import s3
from services.s3 import S3Service
from utils.helpers import decode_photo

s3 = S3Service()


class ProviderManager(BaseManager):
    model = ServiceProviderModel

    @classmethod
    def get_provider(
        cls, status: Optional[str] = None, provider_id: Optional[int] = None
    ) -> List[ServiceProviderModel]:
        """
        Retrieves a service provider based on the provided status and provider ID.

        :param status: The status to filter the provider (e.g., active).
        :param provider_id: The ID of the provider to retrieve.
        :return: A list of service providers matching the criteria.
        """
        return cls.get_records(status=status, record_id=provider_id)

    @classmethod
    def create_provider(cls, data: dict) -> ServiceProviderModel:
        """
        Creates a new service provider from the provided data.

        :param data: A dictionary containing provider data, including an inquiry ID and photo.
        :return: The created ServiceProviderModel instance.
        :raises Forbidden: If the associated inquiry is not approved.
        :raises Conflict: If a provider with the same UIC or Inquiry ID already exists.
        """
        inquiry_id = data.get("inquiry_id")
        inquiry = cls._get_inquiry(inquiry_id)
        encoded_photo = data.pop("photo")
        extension = data.pop("photo_extension")
        name = f"{str(uuid.uuid4())}.{extension}"
        path = os.path.join(TEMP_FILE_FOLDER, f"{name}")
        decode_photo(path, encoded_photo)
        url = s3.upload_photo(path, name, extension)
        data["photo_url"] = url

        if inquiry.status != ProviderRegistrationState.APPROVED:
            raise Forbidden("Inquiry must be approved before registering a provider.")

        try:
            provider = cls.create(data)
            return provider
        except IntegrityError:
            db.session.rollback()
            raise Conflict("A provider with the same UIC or Inquiry ID already exists.")

    @classmethod
    def update_provider(cls, provider_id: int, data: dict) -> None:
        """
        Updates an existing service provider with the provided data.

        :param provider_id: The ID of the provider to update.
        :param data: A dictionary containing updated provider data.
        :return: The updated ServiceProviderModel instance.
        """
        cls.update(provider_id, data)

    @classmethod
    def deactivate_provider(cls, provider_id: int) -> None:
        """
        Deactivates a service provider by its ID.

        :param provider_id: The ID of the provider to deactivate.
        :return: The deactivated ServiceProviderModel instance.
        :raises NotFound: If the provider does not exist.
        """
        provider = cls.get_records(record_id=provider_id)[0]
        cls._deactivate_provider(provider)

    @staticmethod
    def _deactivate_provider(provider: ServiceProviderModel) -> None:
        """
        Marks the given provider as inactive.

        :param provider: The ServiceProviderModel instance to deactivate.
        :return: The deactivated ServiceProviderModel instance.
        """
        provider.is_active = False
        db.session.add(provider)
        db.session.flush()
        # TODO: Implement additional logic to deactivate associated owners, employees, and services.

    @staticmethod
    def _get_inquiry(inquiry_id: int) -> InquiryModel:
        """
        Retrieves an inquiry by its ID.

        :param inquiry_id: The ID of the inquiry to retrieve.
        :return: The InquiryModel instance.
        :raises NotFound: If the inquiry does not exist.
        """
        inquiry = db.session.execute(
            db.select(InquiryModel).filter_by(id=inquiry_id)
        ).scalar_one_or_none()

        if not inquiry:
            raise NotFound(f"Inquiry with ID {inquiry_id} not found.")
        return inquiry
