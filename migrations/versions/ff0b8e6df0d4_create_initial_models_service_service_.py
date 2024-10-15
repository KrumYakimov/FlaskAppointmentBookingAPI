"""create initial models - service,service_category,service_sub_category,junctions

Revision ID: ff0b8e6df0d4
Revises: 32bdbaee62b5
Create Date: 2024-10-15 18:17:24.708963

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff0b8e6df0d4'
down_revision = '32bdbaee62b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('service_providers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_name', sa.String(length=100), nullable=False),
    sa.Column('trade_name', sa.String(length=100), nullable=False),
    sa.Column('uic', sa.String(length=20), nullable=False),
    sa.Column('inquiry_id', sa.Integer(), nullable=True),
    sa.Column('country', sa.String(length=2), nullable=False),
    sa.Column('district', sa.String(length=50), nullable=True),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('neighborhood', sa.String(length=50), nullable=True),
    sa.Column('street', sa.String(length=50), nullable=False),
    sa.Column('street_number', sa.String(length=15), nullable=False),
    sa.Column('block_number', sa.String(length=15), nullable=True),
    sa.Column('apartment', sa.String(length=15), nullable=True),
    sa.Column('floor', sa.String(length=10), nullable=True),
    sa.Column('postal_code', sa.String(length=20), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['inquiry_id'], ['inquiries.id'], name='fk_service_providers_inquiries'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uic')
    )
    op.create_table('subcategories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_subcategories_categories'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('owner_service_provider_association',
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('service_provider_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['service_provider_id'], ['service_providers.id'], ),
    sa.PrimaryKeyConstraint('owner_id', 'service_provider_id')
    )
    op.create_table('services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('service_subcategory_id', sa.Integer(), nullable=False),
    sa.Column('service_provider_id', sa.Integer(), nullable=False),
    sa.Column('staff_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['service_provider_id'], ['service_providers.id'], name='fk_services_service_providers'),
    sa.ForeignKeyConstraint(['service_subcategory_id'], ['subcategories.id'], name='fk_services_subcategories'),
    sa.ForeignKeyConstraint(['staff_id'], ['users.id'], name='fk_services_users'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_provider_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_users_service_provider', 'service_providers', ['service_provider_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_service_provider', type_='foreignkey')
        batch_op.drop_column('service_provider_id')

    op.drop_table('services')
    op.drop_table('owner_service_provider_association')
    op.drop_table('subcategories')
    op.drop_table('service_providers')
    op.drop_table('categories')
    # ### end Alembic commands ###