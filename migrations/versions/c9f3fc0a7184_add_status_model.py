"""add status model

Revision ID: c9f3fc0a7184
Revises: 8c1a4e9b5dfc
Create Date: 2024-07-19 17:43:45.367784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9f3fc0a7184'
down_revision = '8c1a4e9b5dfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('s_name', sa.String(length=200), nullable=True),
    sa.Column('s_name_code', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='assets'
    )
 # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('status', schema='assets')
    # ### end Alembic commands ###