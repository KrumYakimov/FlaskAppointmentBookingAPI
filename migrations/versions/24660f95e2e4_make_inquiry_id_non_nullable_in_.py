"""Make inquiry_id non-nullable in ServiceProviderModel

Revision ID: 24660f95e2e4
Revises: b51a575c3e51
Create Date: 2024-10-29 16:04:02.052943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24660f95e2e4'
down_revision = 'b51a575c3e51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_providers', schema=None) as batch_op:
        batch_op.alter_column('inquiry_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_providers', schema=None) as batch_op:
        batch_op.alter_column('inquiry_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###
