"""Make category_id non-nullable in ServiceSubcategoryModel

Revision ID: 67edd7d6f768
Revises: d2dafcafb67f
Create Date: 2024-10-31 11:12:45.685061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67edd7d6f768'
down_revision = 'd2dafcafb67f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subcategories', schema=None) as batch_op:
        batch_op.alter_column('category_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subcategories', schema=None) as batch_op:
        batch_op.alter_column('category_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###