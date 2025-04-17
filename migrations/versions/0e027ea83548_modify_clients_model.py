"""modify clients model

Revision ID: 0e027ea83548
Revises: 0be17a04b590
Create Date: 2025-04-17 23:58:15.857531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e027ea83548'
down_revision = '0be17a04b590'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clients', schema='assets') as batch_op:
        batch_op.add_column(sa.Column('c_address', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('c_status', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clients', schema='assets') as batch_op:
        batch_op.drop_column('c_status')
        batch_op.drop_column('c_address')

    # ### end Alembic commands ###
