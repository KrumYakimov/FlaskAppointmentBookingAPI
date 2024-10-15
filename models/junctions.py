from db import db

# This junction table links the service providers with their owners in a many-to-many relationship.
owner_service_provider_association = db.Table(
    'owner_service_provider_association',
    db.Column('owner_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('service_provider_id', db.Integer, db.ForeignKey('service_providers.id'), primary_key=True)
)
