from datetime import time

import factory
from faker import Faker
from random import randint
from models import UserModel, RoleType, ServiceProviderModel, InquiryModel, ProviderRegistrationState, AppointmentModel, \
    ServiceCategoryModel, ServiceSubcategoryModel, ServiceModel, WorkingHoursModel
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
    class Meta:
        abstract = True  # Ensure this factory is not directly instantiated

    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.LazyAttribute(lambda _: f"user_{fake.first_name().lower()}.{fake.last_name().lower()}@example.com")
    phone = factory.LazyAttribute(lambda _: f"0{randint(100000000, 999999999)}")
    password = factory.LazyAttribute(lambda _: fake.password())
    is_active = True


class UserFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    # id = factory.Sequence(lambda n: n)  # Starting from 1 for user IDs
    role = RoleType.CLIENT


class AdminFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    # id = factory.Sequence(lambda n: n)
    role = RoleType.ADMIN


class ApproverFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    # id = factory.Sequence(lambda n: n)
    role = RoleType.APPROVER


class OwnerFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    # id = factory.Sequence(lambda n: n)
    role = RoleType.OWNER


class StaffFactory(BaseUserFactory):
    class Meta:
        model = UserModel

    # id = factory.Sequence(lambda n: n)
    role = RoleType.STAFF


class ServiceProviderFactory(BaseFactory):
    class Meta:
        model = ServiceProviderModel

    id = factory.Sequence(lambda n: n)
    company_name = factory.Faker("company")
    trade_name = factory.Faker("company_suffix")
    uic = factory.Sequence(lambda n: f"UIC{n:04}")
    photo_url = factory.LazyAttribute(lambda _: "https://mock-s3-url.com/photo.jpg")  # Placeholder URL

    # Address fields
    country = factory.Faker("country_code")  # No length argument needed
    district = factory.Faker("city")
    city = factory.Faker("city")
    neighborhood = factory.Faker("street_name")
    street = factory.Faker("street_name")
    street_number = factory.Faker("building_number")
    block_number = factory.Faker("building_number")  # Removed nullable
    apartment = factory.Faker("building_number")  # Removed nullable
    floor = factory.Faker("random_int", min=0, max=10)  # Removed nullable
    postal_code = factory.Faker("postcode")
    latitude = factory.Faker("latitude")  # Removed nullable
    longitude = factory.Faker("longitude")  # Removed nullable


class InquiryFactory(BaseFactory):
    class Meta:
        model = InquiryModel

    id = factory.Sequence(lambda n: n)
    salon_name = factory.LazyAttribute(lambda _: fake.company())
    city = factory.LazyAttribute(lambda _: fake.city())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    phone = factory.LazyAttribute(lambda _: f"0{randint(100000000, 999999999)}")
    status = ProviderRegistrationState.APPROVED.name


class AppointmentFactory(BaseFactory):
    class Meta:
        model = AppointmentModel

    id = factory.Sequence(lambda n: n)
    service_id = factory.Sequence(lambda n: n)
    staff_id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    appointment_time = factory.LazyAttribute(lambda _: fake.date_time_this_month())


class CategoryFactory(BaseFactory):
    class Meta:
        model = ServiceCategoryModel

    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda _: fake.word())
    is_active = True


class SubCategoryFactory(BaseFactory):
    class Meta:
        model = ServiceSubcategoryModel

    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda _: fake.word())
    category_id = factory.LazyFunction(lambda: CategoryFactory().id)
    is_active = True


class ServiceFactory(BaseFactory):
    class Meta:
        model = ServiceModel

    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda _: fake.word())
    duration = 30  # Fixed duration of 30 minutes
    price = factory.LazyAttribute(lambda x: round(randint(10, 100), 2))
    service_subcategory_id = factory.LazyFunction(lambda: SubCategoryFactory().id)
    service_provider_id = factory.LazyFunction(lambda: ServiceProviderFactory().id)
    staff_id = factory.LazyFunction(lambda: StaffFactory().id)  # Use appropriate factory for staff
    is_active = True


class WorkingHourFactory(BaseFactory):
    class Meta:
        model = WorkingHoursModel

    day_of_week = factory.LazyAttribute(lambda _: randint(0, 6))  # Random day of the week
    start_time = factory.LazyAttribute(lambda _: time(randint(9, 17), 0))  # Random time from 09:00 to 17:00
    end_time = factory.LazyAttribute(lambda x: time(x.start_time.hour + 1, 0))  # One hour later
    is_active = True
    provider_id = factory.LazyAttribute(lambda x: ServiceProviderFactory().id)
    employee_id = factory.LazyAttribute(lambda x: UserFactory(role='STAFF').id)  # Assuming role is required




