"""Add photo_url to ServiceProviderModel

Revision ID: 7a9b60078eab
Revises: 66726e480e7f
Create Date: 2024-11-03 07:51:51.326965

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a9b60078eab'
down_revision = '66726e480e7f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_providers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo_url', sa.String(length=255), nullable=False, server_default=''))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_providers', schema=None) as batch_op:
        batch_op.drop_column('photo_url')
    # ### end Alembic commands ###

    # ### end Alembic commands ###
