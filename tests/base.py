# from flask_testing import TestCase
#
# from config import create_app
# from db import db
# from tests.constants import TEST_CONFIGURATION
#
#
# class BaseTestCase(TestCase):
#     _HEADER_CONT_TYPE_JSON = {"Content-Type": "application/json"}
#
#     def create_app(self):
#         app = create_app(TEST_CONFIGURATION)
#
#         @app.after_request
#         def return_response(response):
#             db.session.commit()
#             return response
#
#         return app
#
#     def setUp(self):
#         db.init_app(self.app)
#         db.create_all()
#
#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()
#
#
#
from app import environment
from config import create_app
from db import db
from managers.auth_manager import AuthManager
from flask_testing import TestCase

from models import UserModel


class BaseTestCase(TestCase):
    _HEADER_CONT_TYPE_JSON = {"Content-Type": "application/json"}

    def create_app(self):
        return create_app(environment)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
#
#     # from config import create_app
#     # from db import db
#     # from flask_testing import TestCase
#     #
#     # class BaseTestCase(TestCase):
#     #     _HEADER_CONT_TYPE_JSON = {"Content-Type": "application/json"}
#     #
#     #     def create_app(self):
#     #         app = create_app("config.TestingConfig")  # Ensure the testing configuration is correctly set
#     #         return app
#     #
#     #     def setUp(self):
#     #         # Ensure the app context is pushed before creating the database
#     #         with self.app.app_context():
#     #             db.create_all()  # Create all tables
#     #
#     #     def tearDown(self):
#     #         with self.app.app_context():
#     #             db.session.remove()  # Clean up the session
#     #             db.drop_all()  # Drop all tables after each test
#
# #     def register_client(self) -> tuple[str, str]:
# #         # Client registration data
# #         data = {
# #             "email": "client_1@example.com",
# #             "password": "Qwe123!@",
# #             "first_name": "Client",
# #             "last_name": "Tester",
# #             "phone": "0885908117",
# #         }
# #
# #         # Check that there are no clients initially
# #         clients = UserModel.query.all()
# #         self.assertEqual(len(clients), 0)
# #
# #         # Make a POST request to register the client
# #         resp = self.client.post("/clients", json=data)
# #
# #         # Assert the response status code and structure
# #         self.assertEqual(resp.status_code, 201)
# #         token = resp.json["token"]
# #         self.assertIsNotNone(token)
# #
# #         return data["email"], data["password"]  # Returning the email and password for further use
# #
# #     def test_client_registration(self):
# #         email, password = self.register_client()
# #
# #         # Assert that the client was added to the database
# #         client = UserModel.query.filter_by(email=email).first()
# #         self.assertIsNotNone(client)
# #         self.assertEqual(client.email, email)