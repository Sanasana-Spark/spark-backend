"""update user

Revision ID: 60eae5b7a5e6
Revises: 46f9a234ac02
Create Date: 2025-02-20 02:17:59.782438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60eae5b7a5e6'
down_revision = '46f9a234ac02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema='users') as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema='users') as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###
