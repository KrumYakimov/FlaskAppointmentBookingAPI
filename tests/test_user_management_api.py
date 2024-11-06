from random import randint
from unittest.mock import patch

from db import db
from models import UserModel, RoleType, ProviderRegistrationState
from services.s3 import S3Service
from tests.base import BaseTestCase
from tests.constants import Endpoints, ENCODED_PICTURE
from tests import helpers as test_helpers
from tests.factories import AdminFactory, UserFactory, ApproverFactory, InquiryFactory, ServiceProviderFactory
from tests.helpers import generate_token, mock_uuid


class TestCustomerRegistration(BaseTestCase):
    URL = Endpoints.REGISTER_CLIENT[0]
    VALID_CUSTOMER_DATA = {
        "email": "client_1@example.com",
        "password": "Qwe123!@",
        "first_name": "Client",
        "last_name": "Tester",
        "phone": "0885908117",
    }

    def test_customer_registration_success(self):
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=self.VALID_CUSTOMER_DATA)
        self.assertEqual(201, resp.status_code)
        self.assertIn("token", resp.json)
        test_helpers.assert_count_equal(1, UserModel)

    def test_first_name_length(self):
        data = {**self.VALID_CUSTOMER_DATA, "first_name": "A"}
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=data)

        self.assertEqual(400, resp.status_code)
        self.assertIn("Invalid payload", resp.json["message"])
        self.assertIn("First name must be between 2 and 50 characters.", resp.json["message"])

    def test_invalid_email_format(self):
        data = {**self.VALID_CUSTOMER_DATA, "email": "invalid_email"}
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=data)

        self.assertEqual(400, resp.status_code)
        self.assertIn("Invalid payload", resp.json["message"])
        self.assertIn("Invalid email format.", resp.json["message"])

    def test_invalid_first_name_characters(self):
        data = {**self.VALID_CUSTOMER_DATA, "first_name": "Client123"}
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=data)

        self.assertEqual(400, resp.status_code)
        self.assertIn("Invalid payload", resp.json["message"])
        self.assertIn("First name must contain only letters.", resp.json["message"])

    def test_invalid_phone_format(self):
        data = {**self.VALID_CUSTOMER_DATA, "phone": "123456"}
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=data)

        self.assertEqual(400, resp.status_code)
        self.assertIn("Invalid payload", resp.json["message"])
        self.assertIn("Phone number must start with 0 and contain exactly 10 to 15 digits.", resp.json["message"])

    def test_missing_email(self):
        data = {**self.VALID_CUSTOMER_DATA, "email": ""}
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=data)

        self.assertEqual(400, resp.status_code)
        self.assertIn("Invalid payload", resp.json["message"])
        self.assertIn("Not a valid email address.", resp.json["message"])

    def test_missing_first_name(self):
        data = {**self.VALID_CUSTOMER_DATA, "first_name": ""}
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=data)

        self.assertEqual(400, resp.status_code)
        self.assertIn("Invalid payload", resp.json["message"])
        self.assertIn("first_name", resp.json["message"])

    def test_missing_password(self):
        data = {**self.VALID_CUSTOMER_DATA, "password": ""}
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=data)

        self.assertEqual(400, resp.status_code)
        self.assertIn("Invalid payload", resp.json["message"])
        self.assertIn("Password is required.", resp.json["message"])

    def test_missing_phone(self):
        data = {**self.VALID_CUSTOMER_DATA, "phone": ""}
        resp = self.client.post(self.URL, headers=self._HEADER_CONT_TYPE_JSON, json=data)

        self.assertEqual(400, resp.status_code)
        self.assertIn("Invalid payload", resp.json["message"])
        self.assertIn("phone", resp.json["message"])


class TestUserRegistrationPermissions(BaseTestCase):
    URL = Endpoints.REGISTER_USER[0]

    @staticmethod
    def generate_valid_user_data(role):
        return {
            "email": f"user_{randint(1000, 9999)}@example.com",  # Unique email
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "phone": f"0{randint(100000000, 999999999)}",  # Unique phone number
            "role": role
        }

    @staticmethod
    def create_inquiry():
        """Helper method to create an approved inquiry."""
        inquiry = InquiryFactory(status=ProviderRegistrationState.APPROVED)
        return inquiry

    @staticmethod
    def create_service_provider(inquiry):
        """Helper method to create a service provider linked to the given inquiry."""
        provider_data = {
            "company_name": "Delux Ltd",
            "trade_name": "Delux Beauty Center",
            "uic": "1234567877",
            "photo_url": "https://mock-s3-url.com/photo.jpg",
            "inquiry_id": inquiry.id,
            "country": "BG",
            "district": "Sofia",
            "city": "Sofia",
            "neighborhood": "Ivan Vazov",
            "street": "Ivan Vazov",
            "street_number": "17A",
            "block_number": "127A",
            "apartment": "10A",
            "floor": "7",
            "postal_code": "1000",
            "latitude": 45.7262305,
            "longitude": 21.3010148
        }

        provider = ServiceProviderFactory(**provider_data)
        db.session.commit()
        return provider

    def test_admin_can_register_users(self):
        admin_user = AdminFactory()
        token = generate_token(admin_user)
        headers = {"Authorization": f"Bearer {token}"}

        inquiry = self.create_inquiry()
        self.create_service_provider(inquiry)

        for role in ["ADMIN", "APPROVER", "OWNER", "STAFF"]:
            data = self.generate_valid_user_data(role)

            if role == "STAFF":
                data["service_provider_id"] = 1
            elif role == "OWNER":
                data["owned_company_ids"] = [1]

            resp = self.client.post(self.URL, headers=headers, json=data)
            self.assertEqual(resp.status_code, 201)
            self.assertIn("message", resp.json)
            self.assertEqual(resp.json["message"], f"A user with the role of {role} has been registered successfully.")

    def test_approver_can_register_staff_and_owners(self):
        approver_user = ApproverFactory()
        token = generate_token(approver_user)
        headers = {"Authorization": f"Bearer {token}"}

        inquiry = self.create_inquiry()
        self.create_service_provider(inquiry)

        for role in ["OWNER", "STAFF"]:
            data = self.generate_valid_user_data(role)

            if role == "STAFF":
                data["service_provider_id"] = 1
            elif role == "OWNER":
                data["owned_company_ids"] = [1]

            resp = self.client.post(self.URL, headers=headers, json=data)
            self.assertEqual(201, resp.status_code)
            self.assertIn("message", resp.json)
            self.assertEqual(resp.json["message"], f"A user with the role of {role} has been registered successfully.")

    def test_approver_cannot_register_admin(self):
        approver_user = UserFactory(role=RoleType.APPROVER)
        token = generate_token(approver_user)
        headers = {"Authorization": f"Bearer {token}"}

        inquiry = self.create_inquiry()
        self.create_service_provider(inquiry)

        data = self.generate_valid_user_data("ADMIN")
        resp = self.client.post(self.URL, headers=headers, json=data)
        self.assertEqual(403, resp.status_code)
        self.assertIn("message", resp.json)
        self.assertEqual(resp.json["message"], "You do not have permission to create users with the role ADMIN.")

    def test_owner_can_only_register_staff(self):
        owner_user = UserFactory(role=RoleType.OWNER)
        token = generate_token(owner_user)
        headers = {"Authorization": f"Bearer {token}"}

        inquiry = self.create_inquiry()
        self.create_service_provider(inquiry)

        # Valid registration for staff
        data = self.generate_valid_user_data("STAFF")
        data["service_provider_id"] = 1
        resp = self.client.post(self.URL, headers=headers, json=data)
        self.assertEqual(201, resp.status_code)
        self.assertIn("message", resp.json)
        self.assertEqual(resp.json["message"], "A user with the role of STAFF has been registered successfully.")

        # Invalid registration for owner or admin
        for role in ["OWNER", "ADMIN"]:
            data = self.generate_valid_user_data(role)

            if role == "STAFF":
                data["service_provider_id"] = 1
            elif role == "OWNER":
                data["owned_company_ids"] = [1]

            resp = self.client.post(self.URL, headers=headers, json=data)
            self.assertEqual(403, resp.status_code)
            self.assertIn("message", resp.json)
            self.assertEqual(resp.json["message"], f"You do not have permission to create users with the role {role}.")

    def test_staff_cannot_register_any_users(self):
        staff_user = UserFactory(role=RoleType.STAFF)
        token = generate_token(staff_user)
        headers = {"Authorization": f"Bearer {token}"}

        inquiry = self.create_inquiry()
        self.create_service_provider(inquiry)

        for role in ["ADMIN", "APPROVER", "OWNER", "STAFF"]:
            data = self.generate_valid_user_data(role)

            if role == "STAFF":
                data["service_provider_id"] = 1
            elif role == "OWNER":
                data["owned_company_ids"] = [1]

            resp = self.client.post(self.URL, headers=headers, json=data)

            # Expect Forbidden status
            self.assertEqual(403, resp.status_code)
            expected_message = f"You do not have permission to create users with the role {role}."
            self.assertIn("message", resp.json)
            self.assertEqual(resp.json["message"], expected_message)

    def test_invalid_role_registration(self):
        """Test that an invalid role cannot be registered by any user."""
        any_user = UserFactory()  # Using any user for testing
        token = generate_token(any_user)
        headers = {"Authorization": f"Bearer {token}"}

        inquiry = self.create_inquiry()
        self.create_service_provider(inquiry)

        data = self.generate_valid_user_data("INVALID_ROLE")
        resp = self.client.post(self.URL, headers=headers, json=data)
        self.assertEqual(400, resp.status_code)
        self.assertIn("message", resp.json)
        self.assertIn("Invalid payload", resp.json["message"])


