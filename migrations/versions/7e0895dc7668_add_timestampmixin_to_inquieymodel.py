"""add TimestampMixin to InquieyModel

Revision ID: 7e0895dc7668
Revises: ff0b8e6df0d4
Create Date: 2024-10-16 12:59:56.104918

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7e0895dc7668'
down_revision = 'ff0b8e6df0d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inquiries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_on', sa.DateTime(), server_default=sa.text("timezone('UTC', now())"), nullable=False))
        batch_op.add_column(sa.Column('updated_on', sa.DateTime(), server_default=sa.text("timezone('UTC', now())"), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inquiries', schema=None) as batch_op:
        batch_op.drop_column('updated_on')
        batch_op.drop_column('created_on')

    # ### end Alembic commands ###