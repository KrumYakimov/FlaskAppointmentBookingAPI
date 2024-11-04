import os
import uuid

from constants import TEMP_FILE_FOLDER
from db import db
from managers.base_manager import BaseManager
from models import ServiceProviderModel, InquiryModel, ProviderRegistrationState
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, Conflict, Forbidden

from services import s3
from services.s3 import S3Service
from utils.helpers import decode_photo

s3 = S3Service()


class ProviderManager(BaseManager):
    model = ServiceProviderModel

    @classmethod
    def get_provider(cls, status=None, provider_id=None):
        return cls.get_records(status=status, record_id=provider_id)

    @classmethod
    def create_provider(cls, data):
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
