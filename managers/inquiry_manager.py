from typing import Optional, List

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

from db import db
from models import InquiryModel, ProviderRegistrationState
from utils.custom_validators import UniqueConstraintValidator


class InquiryManager:
    @staticmethod
    def register_inquiry(data: dict) -> int:
        """
        Registers a new inquiry with the provided data and sets the status to PENDING.

        :param data: A dictionary containing the inquiry data.
        :return: The ID of the newly created inquiry.
        :raises IntegrityError: If there is a conflict due to unique constraints.
        """
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
    def get_inquiries(status: Optional[str] = None) -> List[InquiryModel]:
        """
        Retrieves inquiries based on the provided status.

        :param status: The status to filter inquiries (e.g., PENDING, APPROVED).
                       If None, fetch all inquiries.
        :return: A list of inquiries matching the status.
        :raises BadRequest: If the status is invalid.
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
    def _validate_inquiry_status(status: str) -> ProviderRegistrationState:
        """
        Validates the inquiry status and returns the corresponding enum value.

        :param status: The status to validate.
        :return: The corresponding ProviderRegistrationState enum value.
        :raises BadRequest: If the status is invalid.
        """
        try:
            return ProviderRegistrationState[status.upper()]
        except KeyError:
            raise BadRequest(f"Invalid status '{status}'")

    @staticmethod
    def update_inquiry_status(
        inquiry_id: int, new_status: ProviderRegistrationState
    ) -> None:
        """
        Updates the status of an existing inquiry.

        :param inquiry_id: The ID of the inquiry to update.
        :param new_status: The new status to set for the inquiry.
        :raises NotFound: If the inquiry does not exist.
        :raises Forbidden: If the status transition is not allowed.
        """
        inquiry = db.session.execute(
            db.select(InquiryModel).filter_by(id=inquiry_id)
        ).scalar_one_or_none()

        if inquiry is None:
            raise NotFound(f"Inquiry with id {inquiry_id} does not exist")

        allowed_transitions = {
            ProviderRegistrationState.PENDING: {
                ProviderRegistrationState.APPROVED,
                ProviderRegistrationState.REJECTED,
            },
            ProviderRegistrationState.APPROVED: {ProviderRegistrationState.NO_SHOW},
        }

        if new_status not in allowed_transitions.get(inquiry.status, {}):
            raise Forbidden(
                "You do not have permissions to change the status of the inquiry"
            )

        inquiry.status = new_status
        db.session.add(inquiry)
        db.session.flush()

    @staticmethod
    def approve_inquiry(inquiry_id: int) -> None:
        """
        Approves an existing inquiry.

        :param inquiry_id: The ID of the inquiry to approve.
        """
        return InquiryManager.update_inquiry_status(
            inquiry_id, ProviderRegistrationState.APPROVED
        )

    @staticmethod
    def reject_inquiry(inquiry_id: int) -> None:
        """
        Rejects an existing inquiry.

        :param inquiry_id: The ID of the inquiry to reject.
        """
        return InquiryManager.update_inquiry_status(
            inquiry_id, ProviderRegistrationState.REJECTED
        )

    @staticmethod
    def no_show_inquiry(inquiry_id: int) -> None:
        """
        Marks an inquiry as a no-show.

        :param inquiry_id: The ID of the inquiry to mark as no-show.
        """
        return InquiryManager.update_inquiry_status(
            inquiry_id, ProviderRegistrationState.NO_SHOW
        )
