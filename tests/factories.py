import factory
from faker import Faker
from random import randint
from models import UserModel, RoleType, ServiceProviderModel, InquiryModel, ProviderRegistrationState
from db import db

fake = Faker()

class BaseFactory(factory.Factory):
    @classmethod
    def create(cls, **kwargs):
        obj = super().create(**kwargs)
        db.session.add(obj)
        db.session.flush()
        return obj


class BaseUserFactory(BaseFactory):
    first_name = factory.LazyAttribute(lambda x: fake.first_name())
    last_name = factory.LazyAttribute(lambda x: fake.last_name())
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    phone = factory.LazyAttribute(lambda x: f"0{randint(100000000, 999999999)}")
    password = factory.LazyAttribute(lambda x: fake.password())

class UserFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n + 10)
    role = RoleType.CLIENT


class AdminFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n + 10)
    role = RoleType.ADMIN


class ApproverFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n + 10)
    role = RoleType.APPROVER


class OwnerFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n + 10)
    role = RoleType.OWNER


class StaffFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n + 10)
    role = RoleType.STAFF


class ServiceProviderFactory(BaseFactory):
    class Meta:
        model = ServiceProviderModel

    id = factory.Sequence(lambda n: n + 1)
    company_name = factory.Faker("company")
    trade_name = factory.Faker("company_suffix")
    uic = factory.Sequence(lambda n: f"UIC{n:04}")
    photo_url = factory.LazyAttribute(lambda x: "https://mock-s3-url.com/photo.jpg")  # Placeholder URL

    # Address fields - you may want to customize these based on your application's needs
    country = factory.Faker("country_code", length=2)
    district = factory.Faker("city")
    city = factory.Faker("city")
    neighborhood = factory.Faker("street_name")
    street = factory.Faker("street_name")
    street_number = factory.Faker("building_number")
    block_number = factory.Faker("building_number", nullable=True)
    apartment = factory.Faker("building_number", nullable=True)
    floor = factory.Faker("random_int", min=0, max=10, nullable=True)
    postal_code = factory.Faker("postcode")
    latitude = factory.Faker("latitude", nullable=True)
    longitude = factory.Faker("longitude", nullable=True)



class InquiryFactory(BaseFactory):
    class Meta:
        model = InquiryModel

    id = factory.Sequence(lambda n: n + 1)
    salon_name = factory.LazyAttribute(lambda _: fake.company())  # Use fake.company() instead of fake.salon_name()
    city = factory.LazyAttribute(lambda _: fake.city())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    phone = factory.LazyAttribute(lambda _: f"0{randint(100000000, 999999999)}")
    status = ProviderRegistrationState.APPROVED.name  # Ensure it's set to the correct enum value as string
