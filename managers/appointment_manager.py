from datetime import timedelta, datetime

from werkzeug.exceptions import NotFound, Conflict, Forbidden

from db import db
from managers.service_manager import ServiceManager
from managers.working_hours_manager import WorkingHoursManager
from models import AppointmentModel, AppointmentState


class AppointmentManager:
    @staticmethod
    def get_available_slots(staff_id, service_duration, date_str):
        """Retrieve available time slots for a given employee on a specific date."""
        try:
            date = datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError("Invalid date format. Please use ISO format.")

        # Get the day of the week (0=Monday, 6=Sunday)
        day_of_week = date.weekday()

        # Retrieve working hours for the employee for that specific day
        working_hours = WorkingHoursManager.get_working_hours(staff_id=staff_id)

        # Filter working hours to get only those relevant for the specific day
        daily_working_hours = [
            wh for wh in working_hours if wh.day_of_week == day_of_week
        ]

        # Retrieve existing appointments for the employee on the specified date
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

        # Loop through the daily working hours to calculate available slots
        for hours in daily_working_hours:
            start_time = datetime.combine(date.date(), hours.start_time)
            end_time = datetime.combine(date.date(), hours.end_time)

            # Create a list of time slots based on working hours and service duration
            while start_time + timedelta(minutes=service_duration) <= end_time:
                slot_start = start_time
                slot_end = start_time + timedelta(minutes=service_duration)

                # Check if the slot overlaps with existing appointments
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
        return db.session.execute(db.select(AppointmentModel)).scalars().all()

    @staticmethod
    def create(data, current_user):
        staff_id = data.get("staff_id")
        appointment_time_str = data.get("appointment_time")

        # Convert appointment_time from string to datetime object
        try:
            appointment_time = datetime.fromisoformat(appointment_time_str)
        except ValueError:
            raise ValueError("Invalid appointment time format. Please use ISO format.")

        service_id = data.get("service_id")

        # Retrieve the service duration using the service_id
        try:
            service_duration = ServiceManager.get_service_duration(service_id)
        except Exception as e:
            print(f"Error retrieving service duration: {e}")  # Debugging log
            raise Conflict("Invalid service ID provided.")

        # Set staff_id and customer_id in data
        data["staff_id"] = staff_id
        data["customer_id"] = current_user.id
        data["appointment_time"] = appointment_time

        # Check if the selected time slot is already booked
        if AppointmentManager.is_slot_booked(
            staff_id, appointment_time, service_duration
        ):
            raise Conflict("The selected time slot is already booked.")

        appointment = AppointmentModel(**data)
        db.session.add(appointment)
        db.session.flush()
        return appointment

    @staticmethod
    def is_slot_booked(staff_id, appointment_time, service_duration):
        # Calculate the end time based on service duration
        end_time = appointment_time + timedelta(minutes=service_duration)

        return (
            db.session.query(AppointmentModel)
            .filter(
                AppointmentModel.staff_id == staff_id,
                AppointmentModel.appointment_time < end_time,
                AppointmentModel.appointment_time + timedelta(minutes=service_duration)
                > appointment_time,
            )
            .count()
            > 0
        )

    @staticmethod
    def update(appointment_id, data):
        appointment = db.session.query(AppointmentModel).get(appointment_id)
        if appointment is None:
            raise NotFound("Appointment not found.")

        for key, value in data.items():
            setattr(appointment, key, value)
        db.session.flush()

    @staticmethod
    def delete(appointment_id):
        appointment = db.session.query(AppointmentModel).get(appointment_id)
        if appointment is None:
            raise NotFound("Appointment not found.")

        db.session.delete(appointment)
        db.session.flush()

    @staticmethod
    def update_appointment_status(appointment_id, current_user, new_status):
        staff_id = current_user.id

        appointment = db.session.execute(
            db.select(AppointmentModel).filter_by(id=appointment_id)
        ).scalar_one_or_none()

        if appointment is None:
            raise NotFound(f"Appointment with id {appointment_id} does not exist")

        allowed_transitions = {
            AppointmentState.PENDING.value: {AppointmentState.CONFIRMED.value, AppointmentState.REJECTED.value},
            AppointmentState.CONFIRMED.value: {AppointmentState.NO_SHOW.value, AppointmentState.CANCELLED.value,
                                               AppointmentState.COMPLETED.value},
        }

        if new_status not in allowed_transitions.get(appointment.status, {}):
            raise Forbidden("You do not have permissions to change the status of the appointment")

        if staff_id != appointment.staff_id:
            raise Forbidden("You do not have permissions to access this resource")

        appointment.status = new_status
        db.session.add(appointment)
        db.session.flush()

    @staticmethod
    def confirm_appointment(appointment_id, current_user):
        return AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.CONFIRMED.value
        )

    @staticmethod
    def reject_appointment(appointment_id, current_user):
        return AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.REJECTED.value
        )

    @staticmethod
    def no_show_inquiry(appointment_id, current_user):
        return AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.NO_SHOW.value
        )

    @staticmethod
    def cancel_appointment(appointment_id, current_user):
        return AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.CANCELLED.value
        )

    @staticmethod
    def complete_appointment(appointment_id, current_user):
        return AppointmentManager.update_appointment_status(
            appointment_id, current_user, AppointmentState.COMPLETED.value
        )
