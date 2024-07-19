"""adjust user class org id

Revision ID: 356eaa06befb
Revises: 412022a0546f
Create Date: 2024-07-16 22:28:45.234467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '356eaa06befb'
down_revision = '412022a0546f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users', schema='users')
    op.create_table('users',
    sa.Column('id', sa.String(), nullable=True),
    sa.Column('default_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('organization_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('default_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('username'),
    schema='users'
    )
 # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users', schema='users')
    # ### end Alembic commands ###