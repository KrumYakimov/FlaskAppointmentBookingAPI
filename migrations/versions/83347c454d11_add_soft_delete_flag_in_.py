"""add soft delete flag in ServiceCategoryModel

Revision ID: 83347c454d11
Revises: d865ea189579
Create Date: 2024-10-30 14:48:37.207904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83347c454d11'
down_revision = 'd865ea189579'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'is_active',
                sa.Boolean(),
                nullable=False,
                server_default=sa.sql.expression.true()
            )
        )

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.alter_column('is_active', server_default=None)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_column('is_active')

    # ### end Alembic commands ###