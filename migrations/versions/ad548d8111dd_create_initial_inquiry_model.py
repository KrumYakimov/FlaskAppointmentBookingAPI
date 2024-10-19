"""create initial inquiry model

Revision ID: ad548d8111dd
Revises: d053e61f6b26
Create Date: 2024-10-15 13:53:29.113321

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ad548d8111dd'
down_revision = 'd053e61f6b26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('inquiries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('salon_name', sa.String(length=100), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('status', sa.Enum('APPROVED', 'PENDING', 'REJECTED', 'NO_SHOW', name='providerregistrationstate'), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('inquiries')
    # ### end Alembic commands ###
