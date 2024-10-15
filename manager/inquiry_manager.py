from werkzeug.exceptions import BadRequest

from db import db
from models import InquiryModel, ProviderRegistrationState


class InquiryManager:
    @staticmethod
    def register_inquiry(data: dict):
        data["status"] = ProviderRegistrationState.PENDING.name
        print(f"Data being passed: {data}")
        inquiry = InquiryModel(**data)
        try:
            db.session.add(inquiry)
            db.session.flush()
            return inquiry.id
        except Exception as ex:
            print(f"Error during registration: {str(ex)}")
            raise BadRequest(f"Error during registration: {str(ex)}")
