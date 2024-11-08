import logging
from datetime import timedelta, datetime

from botocore.exceptions import ClientError
from werkzeug.exceptions import NotFound, Conflict, Forbidden, BadRequest

from db import db
from managers.service_manager import ServiceManager
from managers.working_hours_manager import WorkingHoursManager
from models import AppointmentModel, AppointmentState, UserModel
from services.ses import SESService
from utils.email_templates import EmailTemplates

ses_service = SESService()


class AppointmentManager:
    ONE_DAY_BEFORE = timedelta(days=1)
    TWO_HOURS_BEFORE = timedelta(hours=2)

    @staticmethod
    def get_available_slots(
        staff_id: int, service_duration: int, date_str: str
    ) -> list:
        """
        Retrieves available time slots for a given staff member on a specified date
        :param staff_id: The ID of the staff member.
        :param service_duration: The duration of the service in minutes.
        :param date_str: The date in ISO format for which to retrieve available slots.
        :return: A list of available time slots with start and end times.
        :raises ValueError: If the date format is invalid.
        """
        try:
            date = datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError("Invalid date format. Please use ISO format.")

        day_of_week = date.weekday()

        working_hours = WorkingHoursManager.get_working_hours(staff_id=staff_id)

        daily_working_hours = [
            wh for wh in working_hours if wh.day_of_week == day_of_week
        ]

        existing_appointments = (
            (
                db.session.execute(
                    db.select(AppointmentModel).filter(
                        AppointmentModel.staff_id == staff_id,
                        AppointmentModel.appointment_time >= date,
                        AppointmentModel.appointment_time < date + timedelta(days=1),
                    )
                )
            )
            .scalars()
            .all()
        )

        available_slots = []

        for hours in daily_working_hours:
            start_time = datetime.combine(date.date(), hours.start_time)
            end_time = datetime.combine(date.date(), hours.end_time)

            while start_time + timedelta(minutes=service_duration) <= end_time:
                slot_start = start_time
                slot_end = start_time + timedelta(minutes=service_duration)

                if not any(
                    (
                        slot_start
                        < appointment.appointment_time
                        + timedelta(minutes=service_duration)
                        and slot_end > appointment.appointment_time
                    )
                    for appointment in existing_appointments
                ):
                    available_slots.append(
                        {
                            "start_time": slot_start.isoformat(),
                            "end_time": slot_end.isoformat(),
                        }
                    )

                start_time += timedelta(minutes=service_duration)

        return available_slots

    @staticmethod
    def get_all():
        """
        Retrieves all appointment records from the database
        :return: A list of all appointments.
        """
        return db.session.execute(db.select(AppointmentModel)).scalars().all()

    @staticmethod
    def create(data: dict, current_user: UserModel) -> AppointmentModel:
        """
        Creates a new appointment record in the database
        :param data: A dictionary containing appointment details such as staff_id, appointment_time, etc.
        :param current_user: The user creating the appointment.
        :return: The created AppointmentModel instance.
        :raises ValueError: If the appointment time format is invalid.
        :raises Conflict: If the selected time slot is already booked or if the service ID is invalid.
        """
        staff_id = data.get("staff_id")
        appointment_time_str = data.get("appointment_time")

        try:
            appointment_time = datetime.fromisoformat(appointment_time_str)
        except ValueError:
            logging.error("Invalid appointment time format.")
            raise ValueError("Invalid appointment time format. Please use ISO format.")

        service_id = data.get("service_id")

        try:
            service_duration = ServiceManager.get_service_duration(service_id)
        except Exception as e:
            logging.error(f"Error retrieving service duration: {e}")
            raise Conflict("Invalid service ID provided.")

        data["staff_id"] = staff_id
        data["customer_id"] = current_user.id
        data["appointment_time"] = appointment_time

        if AppointmentManager.is_slot_booked(
            staff_id, appointment_time, service_duration
        ):
            logging.warning("The selected time slot is already booked.")
            raise Conflict("The selected time slot is already booked.")

        appointment = AppointmentModel(**data)
        db.session.add(appointment)

        try:
            db.session.flush()
            AppointmentManager.notify_staff(appointment, current_user)
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error occurred while creating appointment: {e}")
            raise

        return appointment

    @staticmethod
    def update(
        appointment_id: int, data: dict, current_user: UserModel
    ) -> AppointmentModel:
        """
        Updates an existing appointment record in the database
        :param appointment_id: The ID of the appointment to update.
        :param data: A dictionary containing updated appointment details.
        :param current_user: The user performing the update.
        :return: The updated AppointmentModel instance.
        :raises NotFound: If the appointment does not exist.
        :raises Forbidden: If the appointment cannot be edited due to its current status.
        :raises BadRequest: If the update fails.
        """
        appointment = db.session.execute(
            db.select(AppointmentModel).filter(AppointmentModel.id == appointment_id)
        ).scalar_one_or_none()

        if appointment is None:
            raise NotFound("Appointment not found.")

        editable_statuses = {
            AppointmentState.PENDING.value,
            AppointmentState.CONFIRMED.value,
        }

        if appointment.status not in editable_statuses:
            raise Forbidden("You cannot edit this appointment in its current status.")

        new_appointment_time = data["appointment_time"]
        staff_id = appointment.staff_id
        duration = appointment.service.duration

        if AppointmentManager.is_slot_booked(staff_id, new_appointment_time, duration):
            raise Conflict("The selected time slot is already booked.")

        appointment.appointment_time = datetime.fromisoformat(new_appointment_time)

        appointment.status = AppointmentState.PENDING.value

        content = EmailTemplates.CONTENT_APPOINTMENT_UPDATED.format(
            first_name=current_user.first_name,
            appointment_id=appointment_id,
            service_name=appointment.service.name,
            new_appointment_time=appointment.appointment_time.isoformat(),
            employee_name=f"{appointment.staff.first_name} {appointment.staff.last_name}",
        )

        try:
            AppointmentManager.send_notification_email(
                appointment.customer.email,
                EmailTemplates.SUBJECT_APPOINTMENT_UPDATED,
                content,
                appointment_id,
            )
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating appointment: {e}")
            raise BadRequest("Failed to update appointment.")

        return appointment

    @staticmethod
    def delete(appointment_id: int) -> None:
        """
        Deletes an appointment record from the database
        :param appointment_id: The ID of the appointment to delete.
        :raises NotFound: If the appointment does not exist.
        """
        appointment = db.session.query(AppointmentModel).get(appointment_id)
        if appointment is None:
            raise NotFound("Appointment not found.")

        db.session.delete(appointment)
        db.session.flush()

    @staticmethod
    def update_appointment_status(
        appointment_id: int, current_user: UserModel, new_status: str
    ) -> AppointmentModel:
        """
        Updates the status of an existing appointment
        :param appointment_id: The ID of the appointment to update.
        :param current_user: The user performing the status update.
        :param new_status: The new status to set for the appointment.
        :return: The updated AppointmentModel instance.
        :raises NotFound: If the appointment does not exist.
        :raises Forbidden: If the user does not have permission to change the status.
        """
        staff_id = current_user.id

        appointment = db.session.execute(
            db.select(AppointmentModel).filter_by(id=appointment_id)
        ).scalar_one_or_none()

        if appointment is None:
            raise NotFound(f"Appointment with id {appointment_id} does not exist")

        allowed_transitions = {
            AppointmentState.PENDING.value: {
                AppointmentState.CONFIRMED.value,
                AppointmentState.REJECTED.value,
            },
            AppointmentState.CONFIRMED.value: {
                AppointmentState.NO_SHOW.value,
                AppointmentState.CANCELLED.value,
                AppointmentState.COMPLETED.value,
            },
        }

        if new_status not in allowed_transitions.get(appointment.status, {}):
            raise Forbidden(
                "You do not have permissions to change the status of the appointment"
            )

        if staff_id != appointment.staff_id:
            raise Forbidden("You do not have permissions to access this resource")

        appointment.status = new_status
        db.session.add(appointment)
        db.session.flush()

        return appointment

    @staticmethod
    def confirm_appointment(
        appointment_id: int, current_user: UserModel
    ) -> AppointmentModel:
        """
        Confirms an existing appointment
        :param appointment_id: The ID of the appointment to confirm.
        :param current_user: The user performing the confirmation.
        :return: The confirmed AppointmentModel instance.
        :raises NotFound: If the appointment does not exist.
        :raises BadRequest: If customer information is missing.
        """
        appointment = AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.CONFIRMED.value
        )

        if appointment is None:
            raise NotFound(f"Appointment with ID {appointment_id} does not exist.")

        if appointment.customer is None or not appointment.customer.email:
            raise BadRequest("Customer information is missing or invalid.")

        recipient = appointment.customer.email
        content = EmailTemplates.CONTENT_APPOINTMENT_CONFIRMED.format(
            first_name=appointment.customer.first_name,
            appointment_id=appointment_id,
            service_name=appointment.service.name,
            appointment_time=appointment.appointment_time.isoformat(),
            employee_name=f"{appointment.staff.first_name} {appointment.staff.last_name}",
        )

        try:
            AppointmentManager.send_notification_email(
                recipient,
                EmailTemplates.SUBJECT_APPOINTMENT_CONFIRMED,
                content,
                appointment_id,
            )
        except BadRequest as e:
            db.session.rollback()
            logging.error(
                f"Failed to send confirmation email for appointment {appointment_id}: {e}"
            )
            raise

        return appointment

    @staticmethod
    def reject_appointment(
        appointment_id: int, current_user: UserModel
    ) -> AppointmentModel:
        """
        Rejects an existing appointment
        :param appointment_id: The ID of the appointment to reject.
        :param current_user: The user performing the rejection.
        :return: The rejected AppointmentModel instance.
        :raises NotFound: If the appointment does not exist.
        :raises BadRequest: If customer information is missing.
        """
        appointment = AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.REJECTED.value
        )

        if appointment is None:
            raise NotFound(f"Appointment with ID {appointment_id} does not exist.")

        if appointment.customer is None or not appointment.customer.email:
            raise BadRequest("Customer information is missing or invalid.")

        recipient = appointment.customer.email

        content = EmailTemplates.CONTENT_APPOINTMENT_REJECTED.format(
            first_name=appointment.customer.first_name, appointment_id=appointment_id
        )

        try:
            AppointmentManager.send_notification_email(
                recipient,
                EmailTemplates.SUBJECT_APPOINTMENT_REJECTED,
                content,
                appointment_id,
            )
        except BadRequest as e:
            db.session.rollback()
            logging.error(
                f"Failed to send rejection email for appointment {appointment_id}: {e}"
            )
            raise

        return appointment

    @staticmethod
    def cancel_appointment(
        appointment_id: int, current_user: UserModel
    ) -> AppointmentModel:
        """
        Cancels an existing appointment
        :param appointment_id: The ID of the appointment to cancel.
        :param current_user: The user performing the cancellation.
        :return: The canceled AppointmentModel instance.
        :raises NotFound: If the appointment does not exist.
        :raises BadRequest: If customer information is missing.
        """
        appointment = AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.CANCELLED.value
        )

        if appointment is None:
            raise NotFound(f"Appointment with ID {appointment_id} does not exist.")

        if appointment.customer is None or not appointment.customer.email:
            raise BadRequest("Customer information is missing or invalid.")

        recipient = appointment.customer.email
        subject = "Your Appointment Has Been Canceled"

        content = EmailTemplates.CONTENT_APPOINTMENT_CANCELLED.format(
            first_name=appointment.customer.first_name, appointment_id=appointment_id
        )

        try:
            AppointmentManager.send_notification_email(
                recipient,
                EmailTemplates.SUBJECT_APPOINTMENT_CANCELLED,
                content,
                appointment_id,
            )
        except BadRequest as e:
            db.session.rollback()
            logging.error(
                f"Failed to send cancellation email for appointment {appointment_id}: {e}"
            )
            raise

        return appointment

    @staticmethod
    def no_show_inquiry(
        appointment_id: int, current_user: UserModel
    ) -> AppointmentModel:
        """
        Marks an appointment as a no-show
        :param appointment_id: The ID of the appointment to mark as no-show.
        :param current_user: The user performing the operation.
        :return: The AppointmentModel instance with the no-show status.
        """
        return AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.NO_SHOW.value
        )

    @staticmethod
    def complete_appointment(appointment_id, current_user):
        """
        Marks an appointment as completed
        :param appointment_id: The ID of the appointment to mark as completed.
        :param current_user: The user performing the operation.
        :return: The AppointmentModel instance with the completed status.
        """
        return AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.COMPLETED.value
        )

    @staticmethod
    def notify_staff(appointment: AppointmentModel, current_user: UserModel) -> None:
        """
        Notifies the staff member assigned to an appointment via email
        :param appointment: The AppointmentModel instance to notify staff about.
        :param current_user: The user performing the operation, used to personalize the email.
        :raises BadRequest: If staff information is missing or invalid.
        """
        if appointment.staff is None or not appointment.staff.email:
            raise BadRequest("Staff information is missing for the appointment.")

        staff_email = appointment.staff.email
        content = EmailTemplates.CONTENT_APPOINTMENT_NOTIFIED.format(
            client_name=f"{current_user.first_name} {current_user.last_name}",
            service_name=appointment.service.name,
            appointment_time=appointment.appointment_time.isoformat(),
            employee_name=f"{appointment.staff.first_name} {appointment.staff.last_name}",
        )

        AppointmentManager.send_notification_email(
            staff_email,
            EmailTemplates.SUBJECT_APPOINTMENT_BOOKED,
            content,
            appointment.id,
        )

    @staticmethod
    def send_notification_email(
        recipient: str, subject: str, content: str, appointment_id: int
    ) -> None:
        """
        Sends a notification email
        :param recipient: The email address of the recipient.
        :param subject: The subject line of the email.
        :param content: The body content of the email.
        :param appointment_id: The ID of the appointment associated with the email.
        :raises BadRequest: If sending the email fails.
        """
        try:
            ses_service.send_email(recipient, subject, content)
            logging.info(
                f"Notification email sent to {recipient} for appointment {appointment_id}."
            )
        except ClientError as e:
            logging.error(f"Error occurred while sending email: {e}")
            raise BadRequest("Failed to send notification email.")

    @staticmethod
    def is_slot_booked(
        staff_id: int, appointment_time: datetime, service_duration: int
    ) -> int:
        """
        Checks if a time slot is already booked for a given staff member
        :param staff_id: The ID of the staff member.
        :param appointment_time: The desired appointment time.
        :param service_duration: The duration of the service in minutes.
        :return: True if the slot is booked, otherwise False.
        """
        if isinstance(appointment_time, str):
            appointment_time = datetime.fromisoformat(appointment_time)

        end_time = appointment_time + timedelta(minutes=service_duration)

        overlapping_appointments = (
            db.session.execute(
                db.select(AppointmentModel).filter(
                    AppointmentModel.staff_id == staff_id,
                    AppointmentModel.appointment_time < end_time,
                    AppointmentModel.appointment_time
                    + timedelta(minutes=service_duration)
                    > appointment_time,
                )
            )
            .scalars()
            .all()
        )

        return len(overlapping_appointments) > 0
