from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

from db import db
from models import InquiryModel, ProviderRegistrationState
from utils.custom_validators import UniqueConstraintValidator


class InquiryManager:
    @staticmethod
    def register_inquiry(data: dict):
        data["status"] = ProviderRegistrationState.PENDING.name
        inquiry = InquiryModel(**data)

        validator = UniqueConstraintValidator(db.session)

        try:
            db.session.add(inquiry)
            db.session.flush()
            return inquiry.id
        except IntegrityError as e:
            validator.rollback()
            validator.check_unique_violation(e)

    @staticmethod
    def get_inquiries(status=None):
        """
        Retrieves inquiries based on the provided status.

        :param status: The status to filter inquiries (e.g., PENDING, APPROVED)
        or fetch all inquiries if no status is provided.
        :return: A list of inquiries matching the status.
        """

        if status:
            status_enum = InquiryManager._validate_inquiry_status(status)
            return (
                db.session.execute(
                    db.select(InquiryModel).filter_by(status=status_enum)
                )
                .scalars()
                .all()
            )

        return db.session.execute(db.select(InquiryModel)).scalars().all()

    @staticmethod
    def _validate_inquiry_status(status):
        """
        Validates the status and returns the corresponding enum value.
        Raises BadRequest if the status is invalid.
        """
        try:
            return ProviderRegistrationState[status.upper()]
        except KeyError:
            raise BadRequest(f"Invalid status '{status}'")

    @staticmethod
    def update_inquiry_status(inquiry_id, new_status):
        inquiry = db.session.execute(
            db.select(InquiryModel).filter_by(id=inquiry_id)
        ).scalar_one_or_none()

        if inquiry is None:
            raise NotFound(f"Inquiry with id {inquiry_id} does not exist")

        allowed_transitions = {
            ProviderRegistrationState.PENDING: {
                ProviderRegistrationState.APPROVED,
                ProviderRegistrationState.REJECTED
            },
            ProviderRegistrationState.APPROVED: {
                ProviderRegistrationState.NO_SHOW
            },
        }

        if new_status not in allowed_transitions.get(inquiry.status, {}):
            raise Forbidden("You do not have permissions to change the status of the inquiry")

        inquiry.status = new_status
        db.session.add(inquiry)
        db.session.flush()

    @staticmethod
    def approve_inquiry(inquiry_id):
        return InquiryManager.update_inquiry_status(
            inquiry_id, ProviderRegistrationState.APPROVED
        )

    @staticmethod
    def reject_inquiry(inquiry_id):
        return InquiryManager.update_inquiry_status(
            inquiry_id, ProviderRegistrationState.REJECTED
        )

    @staticmethod
    def no_show_inquiry(inquiry_id):
        return InquiryManager.update_inquiry_status(
            inquiry_id, ProviderRegistrationState.NO_SHOW
        )
