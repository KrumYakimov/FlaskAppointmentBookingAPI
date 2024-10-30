from marshmallow import fields, Schema

from utils.custom_validators import PersonalInfoValidator, AddressFieldValidator


class PersonalInfoSchema(Schema):
    email = PersonalInfoValidator.email()
    first_name = PersonalInfoValidator.first_name()
    last_name = PersonalInfoValidator.last_name()
    phone = PersonalInfoValidator.phone()


class TimestampSchema(Schema):
    created_on = fields.DateTime(dump_only=True)
    updated_on = fields.DateTime(dump_only=True)


class AddressSchema(Schema):
    country = AddressFieldValidator.country()
    district = AddressFieldValidator.district()
    city = AddressFieldValidator.city()
    neighborhood = AddressFieldValidator.neighborhood()
    street = AddressFieldValidator.street()
    street_number = AddressFieldValidator.street_number()
    block_number = AddressFieldValidator.block_number()
    apartment = AddressFieldValidator.apartment()
    floor = AddressFieldValidator.floor()
    postal_code = AddressFieldValidator.postal_code()
    latitude = AddressFieldValidator.latitude()
    longitude = AddressFieldValidator.longitude()
