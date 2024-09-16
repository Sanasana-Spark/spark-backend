"""add trip & operator status model

Revision ID: f08b7d7ee7b0
Revises: c9f3fc0a7184
Create Date: 2024-07-21 14:48:20.370010

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f08b7d7ee7b0'
down_revision = 'c9f3fc0a7184'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ostatus',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('o_name', sa.String(length=200), nullable=True),
    sa.Column('o_name_code', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='assets'
    )
    op.create_table('tstatus',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('t_name', sa.String(length=200), nullable=True),
    sa.Column('t_name_code', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='assets'
    )
 # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tstatus', schema='assets')
    op.drop_table('ostatus', schema='assets')
    # ### end Alembic commands ###