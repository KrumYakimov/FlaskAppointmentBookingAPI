import json
import os
from unittest.mock import patch

from constants import TEMP_FILE_FOLDER
from models import ServiceProviderModel, ProviderRegistrationState
from services.s3 import S3Service
from tests.base import BaseTestCase
from tests.constants import ENCODED_PICTURE, Endpoints
from tests.factories import InquiryFactory, ApproverFactory
from tests.helpers import generate_token, mock_uuid


class TestProviderRegistration(BaseTestCase):
    URL = Endpoints.REGISTER_PROVIDER[0]

    @patch("uuid.uuid4", mock_uuid)
    @patch.object(S3Service, "upload_photo", return_value="https://mock-s3-url.com/photo.jpg")
    def test_create_service_provider(self, mocked_upload):
        approver_user = ApproverFactory()
        token = generate_token(approver_user)

        inquiry = InquiryFactory(status=ProviderRegistrationState.APPROVED)
        data = {
            "company_name": "Delux Ltd",
            "trade_name": "Delux Beauty Center",
            "uic": "1234567877",
            "photo": ENCODED_PICTURE,
            "photo_extension": "png",
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

        resp = self.client.post(
            self.URL,
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        self.assertEqual(resp.status_code, 201)
        self.assertIn("message", resp.json)
        self.assertEqual(resp.json["message"].strip(), "Service Provider created successfully")

        uuid_value = mock_uuid()
        name = f"{uuid_value}.{data['photo_extension']}"
        path = os.path.join(TEMP_FILE_FOLDER, name)

        # Verify that the service provider was created
        providers = ServiceProviderModel.query.all()
        self.assertEqual(len(providers), 1)
        provider = providers[0]
        self.assertEqual(provider.company_name, data["company_name"])
        self.assertEqual(provider.trade_name, data["trade_name"])
        self.assertEqual(provider.uic, data["uic"])
        self.assertEqual(provider.photo_url, mocked_upload.return_value)
        self.assertEqual(provider.inquiry.id, inquiry.id)

        mocked_upload.assert_called_once_with(path, name, data['photo_extension'])
