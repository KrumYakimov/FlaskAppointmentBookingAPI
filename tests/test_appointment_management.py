from datetime import time, datetime, timedelta
from unittest import mock
from unittest.mock import patch

from flask import url_for

from db import db
from models import ProviderRegistrationState, AppointmentState, AppointmentModel
from tests.base import BaseTestCase
from tests.constants import Endpoints
from tests.factories import (
    UserFactory,
    StaffFactory,
    InquiryFactory,
    ServiceProviderFactory,
    CategoryFactory,
    SubCategoryFactory,
    ServiceFactory,
    WorkingHourFactory,
    AppointmentFactory,
)
from tests.helpers import generate_token
from utils.email_templates import EmailTemplates


class TestAppointmentManagement(BaseTestCase):
    URL_BOOKING = Endpoints.CUSTOMER_APPOINTMENT_BOOKING[0]
    URL_AVAILABLE_SLOTS = Endpoints.AVAILABLE_SLOTS[0]
    URL_APPOINTMENTS_INFO = Endpoints.CUSTOMER_APPOINTMENTS_INFO[0]
    URL_APPOINTMENT_EDIT = Endpoints.CUSTOMER_APPOINTMENT_EDITING[0]
    URL_APPOINTMENT_CANCEL = Endpoints.CUSTOMER_APPOINTMENT_CANCELLATION[0]
    URL_APPOINTMENT_CONFIRM = Endpoints.STAFF_APPOINTMENT_CONFIRMATION[0]
    URL_APPOINTMENT_REJECT = Endpoints.STAFF_APPOINTMENT_REJECTION[0]
    URL_APPOINTMENT_NO_SHOW = Endpoints.STAFF_APPOINTMENT_NO_SHOW[0]
    URL_APPOINTMENT_COMPLETE = Endpoints.STAFF_APPOINTMENT_COMPLETION[0]

    def setUp(self):
        super().setUp()
        self.client_user = UserFactory()
        self.staff_user = StaffFactory()

        self.token_client = generate_token(self.client_user)
        self.token_staff = generate_token(self.staff_user)

        self.inquiry = InquiryFactory(status=ProviderRegistrationState.APPROVED)
        self.provider = ServiceProviderFactory(inquiry_id=self.inquiry.id)

        self.category = CategoryFactory()
        self.subcategory = SubCategoryFactory(category_id=self.category.id)

        self.service = ServiceFactory(
            service_subcategory_id=self.subcategory.id,
            service_provider_id=self.provider.id,
        )

        self.working_hour = WorkingHourFactory(
            provider_id=self.provider.id,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    @patch("services.ses.SESService.send_email")
    def test_book_appointment(self, mock_send_email):
        data = {
            "staff_id": self.staff_user.id,
            "service_id": self.service.id,
            "appointment_time": "2024-11-15T13:00:00",
        }

        url = self.URL_BOOKING

        resp = self.client.post(
            url,
            headers={"Authorization": f"Bearer {self.token_client}"},
            json=data,
        )

        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.json)
        self.assertEqual(resp.json["appointment_time"], data["appointment_time"])

        expected_body = EmailTemplates.CONTENT_APPOINTMENT_NOTIFIED.format(
            client_name=f"{self.client_user.first_name} {self.client_user.last_name}",
            service_name=self.service.name,
            appointment_time=data["appointment_time"],
            employee_name=f"{self.staff_user.first_name} {self.staff_user.last_name}",
        ).strip()

        actual_body = mock_send_email.call_args[0][2].strip()
        assert (
            actual_body == expected_body
        ), f"Expected body: '{expected_body}' but got: '{actual_body}'"

    def test_get_available_slots(self):
        date = "2024-11-15"
        staff_id = self.staff_user.id
        service_id = self.service.id

        # url = f"/appointments/available_slots/{staff_id}/{service_id}/{date}"
        url = (
            self.URL_AVAILABLE_SLOTS.replace("<int:staff_id>", str(staff_id))
            .replace("<int:service_id>", str(service_id))
            .replace("<string:date>", date)
        )

        response = self.client.get(
            url, headers={"Authorization": f"Bearer {self.token_client}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("available_slots", response.json)
        self.assertIsInstance(response.json["available_slots"], list)

    def test_customer_appointments_info(self):
        appointment = AppointmentFactory(
            customer_id=self.client_user.id, staff_id=self.staff_user.id
        )

        db.session.add(appointment)
        db.session.commit()

        url = self.URL_APPOINTMENTS_INFO

        response = self.client.get(
            url,
            headers={"Authorization": f"Bearer {self.token_client}"},
        )

        self.assertEqual(response.status_code, 200)

        appointments = response.json

        self.assertTrue(
            any(a["id"] == appointment.id for a in appointments),
            "The created appointment was not found in the response.",
        )

    @patch("services.ses.SESService.send_email")
    def test_edit_appointment(self, mock_send_email):
        appointment = AppointmentFactory(
            customer_id=self.client_user.id,
            staff_id=self.staff_user.id,
            service_id=self.service.id,
        )

        new_appointment_time = "2024-11-15T10:30:00"
        data = {"appointment_time": new_appointment_time}

        # url = f"/appointments/{appointment.id}/edit"
        url = self.URL_APPOINTMENT_EDIT.replace(
            "<int:appointment_id>", str(appointment.id)
        )

        response = self.client.put(
            url,
            headers={"Authorization": f"Bearer {self.token_client}"},
            json=data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Appointment updated successfully")

        expected_body = EmailTemplates.CONTENT_APPOINTMENT_UPDATED.format(
            first_name=self.client_user.first_name,
            appointment_id=appointment.id,
            service_name=appointment.service.name,
            new_appointment_time=new_appointment_time,
            employee_name=f"{self.staff_user.first_name} {self.staff_user.last_name}",  # Ensure full name
        ).strip()

        if mock_send_email.call_args:
            actual_body = mock_send_email.call_args[0][2].strip()
            assert (
                actual_body == expected_body
            ), f"Expected body: '{expected_body}' but got: '{actual_body}'"

    @patch("services.ses.SESService.send_email")
    def test_confirm_appointment(self, mock_send_email):
        appointment = AppointmentFactory(
            customer_id=self.client_user.id,
            staff_id=self.staff_user.id,
            status=AppointmentState.PENDING.value,
        )

        # url = f"/appointments/{appointment.id}/confirm"
        url = self.URL_APPOINTMENT_CONFIRM.replace(
            "<int:appointment_id>", str(appointment.id)
        )

        response = self.client.put(
            url, headers={"Authorization": f"Bearer {self.token_staff}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Appointment confirmed successfully")

        updated_appointment = db.session.execute(
            db.select(AppointmentModel).filter_by(id=appointment.id)
        ).scalar_one_or_none()

        self.assertEqual(updated_appointment.status, AppointmentState.CONFIRMED.value)

        expected_body = EmailTemplates.CONTENT_APPOINTMENT_CONFIRMED.format(
            first_name=appointment.customer.first_name,
            appointment_id=appointment.id,
            service_name=appointment.service.name,
            appointment_time=appointment.appointment_time.isoformat(),
            employee_name=f"{appointment.staff.first_name} {appointment.staff.last_name}",
        ).strip()

        if mock_send_email.call_args:
            actual_body = mock_send_email.call_args[0][2].strip()
            assert (
                actual_body == expected_body
            ), f"Expected body: '{expected_body}' but got: '{actual_body}'"

    @patch("services.ses.SESService.send_email")
    def test_reject_appointment(self, mock_send_email):
        appointment = AppointmentFactory(
            customer_id=self.client_user.id,
            staff_id=self.staff_user.id,
            status=AppointmentState.PENDING.value,
        )

        # url = f"/appointments/{appointment.id}/reject"
        url = self.URL_APPOINTMENT_REJECT.replace(
            "<int:appointment_id>", str(appointment.id)
        )

        response = self.client.put(
            url, headers={"Authorization": f"Bearer {self.token_staff}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Appointment rejected successfully")

        updated_appointment = db.session.execute(
            db.select(AppointmentModel).filter_by(id=appointment.id)
        ).scalar_one_or_none()

        self.assertEqual(updated_appointment.status, AppointmentState.REJECTED.value)

        expected_body = EmailTemplates.CONTENT_APPOINTMENT_REJECTED.format(
            first_name=appointment.customer.first_name,
            appointment_id=appointment.id,
        ).strip()

        if mock_send_email.call_args:
            actual_body = mock_send_email.call_args[0][2].strip()
            assert (
                actual_body == expected_body
            ), f"Expected body: '{expected_body}' but got: '{actual_body}'"

    @patch("services.ses.SESService.send_email")
    def test_cancel_appointment(self, mock_send_email):
        appointment = AppointmentFactory(
            customer_id=self.client_user.id,
            staff_id=self.staff_user.id,
            status=AppointmentState.CONFIRMED.value,
        )

        # url = f"/appointments/{appointment.id}/cancel"
        url = self.URL_APPOINTMENT_CANCEL.replace(
            "<int:appointment_id>", str(appointment.id)
        )

        response = self.client.put(
            url,
            headers={"Authorization": f"Bearer {self.token_staff}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Appointment canceled successfully")

        updated_appointment = db.session.execute(
            db.select(AppointmentModel).filter_by(id=appointment.id)
        ).scalar_one_or_none()

        self.assertEqual(updated_appointment.status, AppointmentState.CANCELLED.value)

        expected_body = EmailTemplates.CONTENT_APPOINTMENT_CANCELLED.format(
            first_name=appointment.customer.first_name,
            appointment_id=appointment.id,
        ).strip()

        if mock_send_email.call_args:
            actual_body = mock_send_email.call_args[0][2].strip()
            assert (
                actual_body == expected_body
            ), f"Expected body: '{expected_body}' but got: '{actual_body}'"

    def test_no_show_appointment(self):
        appointment = AppointmentFactory(
            customer_id=self.client_user.id,
            staff_id=self.staff_user.id,
            status=AppointmentState.CONFIRMED.value,
        )

        # url = f"/appointments/{appointment.id}/no_show"
        url = self.URL_APPOINTMENT_NO_SHOW.replace(
            "<int:appointment_id>", str(appointment.id)
        )

        response = self.client.put(
            url,
            headers={"Authorization": f"Bearer {self.token_staff}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Appointment no showed successfully")

        updated_appointment = db.session.execute(
            db.select(AppointmentModel).filter_by(id=appointment.id)
        ).scalar_one_or_none()

        self.assertEqual(updated_appointment.status, AppointmentState.NO_SHOW.value)

    def test_complete_appointment(self):
        appointment = AppointmentFactory(
            customer_id=self.client_user.id,
            staff_id=self.staff_user.id,
            status=AppointmentState.CONFIRMED.value,
        )

        # url = f"/appointments/{appointment.id}/complete"
        url = self.URL_APPOINTMENT_COMPLETE.replace(
            "<int:appointment_id>", str(appointment.id)
        )

        response = self.client.put(
            url,
            headers={"Authorization": f"Bearer {self.token_staff}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Appointment completed successfully")

        updated_appointment = db.session.execute(
            db.select(AppointmentModel).filter_by(id=appointment.id)
        ).scalar_one_or_none()
        self.assertEqual(updated_appointment.status, AppointmentState.COMPLETED.value)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], AppointmentState.COMPLETED.value)


# from datetime import time
# from unittest import mock
# from unittest.mock import patch
#
# from models import ProviderRegistrationState
# from tests.base import BaseTestCase
# from tests.constants import Endpoints
# from tests.factories import (
#     UserFactory,
#     StaffFactory,
#     InquiryFactory,
#     ServiceProviderFactory,
#     CategoryFactory,
#     SubCategoryFactory,
#     ServiceFactory,
#     WorkingHourFactory,
# )
# from tests.helpers import generate_token
# from utils.email_templates import EmailTemplates
#
#
# class TestAppointmentManagement(BaseTestCase):
#     URL_BOOKING = Endpoints.CUSTOMER_APPOINTMENT_BOOKING[0]
#
#     def setUp(self):
#         super().setUp()
#         self.client_user = UserFactory(email='user_amber.rasmussen@example.com', first_name="amber",
#                                        last_name="rasmussen")
#         self.staff_user = StaffFactory(email='user_alexis.garza@example.com', first_name="alexis", last_name="garza")
#
#         self.token_client = generate_token(self.client_user)
#         self.token_staff = generate_token(self.staff_user)
#
#         self.inquiry = InquiryFactory(status=ProviderRegistrationState.APPROVED)
#         self.provider = ServiceProviderFactory(inquiry_id=self.inquiry.id)
#
#         self.category = CategoryFactory()
#         self.subcategory = SubCategoryFactory(category_id=self.category.id)
#
#         self.service = ServiceFactory(
#             service_subcategory_id=self.subcategory.id, service_provider_id=self.provider.id
#         )
#
#         self.working_hour = WorkingHourFactory(
#             provider_id=self.provider.id,
#             day_of_week=0,
#             start_time=time(9, 0),
#             end_time=time(17, 0)
#         )
#
#         print(f"Working Hours: {self.working_hour.start_time} - {self.working_hour.end_time}")
#         print(f"Staff User Created: {self.staff_user}")
#
#     @patch("services.ses.SESService.send_email")
#     def test_book_appointment(self, mock_send_email):
#         data = {
#             "staff_id": self.staff_user.id,
#             "service_id": self.service.id,
#             "appointment_time": "2024-11-15T13:00:00",
#         }
#
#         resp = self.client.post(
#             self.URL_BOOKING,
#             headers={"Authorization": f"Bearer {self.token_client}"},
#             json=data,
#         )
#
#         # Debugging output
#         print(f"Response Status Code: {resp.status_code}")
#         print(f"Response JSON: {resp.json}")
#
#         # Assertions
#         self.assertEqual(resp.status_code, 201)  # Expect successful booking
#         self.assertIn('id', resp.json)  # Check that an appointment ID is returned
#         self.assertEqual(resp.json['appointment_time'], data['appointment_time'])  # Verify the appointment time
#
#         # Create the expected body
#         # After generating your expected and actual bodies
#         expected_body = EmailTemplates.CONTENT_APPOINTMENT_NOTIFIED.format(
#             client_name=f"{self.client_user.first_name} {self.client_user.last_name}",
#             service_name=self.service.name,
#             appointment_time=data['appointment_time'],
#             employee_name=f"{self.staff_user.first_name} {self.staff_user.last_name}",
#         ).strip()  # Make sure to remove any extra spaces at the start or end
#
#         # Simulate sending the email (the actual body)
#         actual_body = mock_send_email.call_args[0][2].strip()  # Get the body from the mock call
#
#         # Debugging: print out lengths and representations
#         print(f"Length of Expected Body: {len(expected_body)}")
#         print(f"Length of Actual Body: {len(actual_body)}")
#         print(f"Expected Body Representation: {repr(expected_body)}")
#         print(f"Actual Body Representation: {repr(actual_body)}")
#
#         # Check each character to find the difference
#         for i, (expected_char, actual_char) in enumerate(zip(expected_body, actual_body)):
#             if expected_char != actual_char:
#                 print(f"Difference at index {i}: Expected '{expected_char}' Actual '{actual_char}'")
#
#         # Now perform your assertion to check if they are equal
#         assert actual_body == expected_body, f"Expected body: '{expected_body}' but got: '{actual_body}'"
