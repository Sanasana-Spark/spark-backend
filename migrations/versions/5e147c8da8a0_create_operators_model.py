"""create operators model

Revision ID: 5e147c8da8a0
Revises: f46b3340b86c
Create Date: 2024-07-09 14:00:09.831855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e147c8da8a0'
down_revision = 'f46b3340b86c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('operators',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('o_name', sa.String(length=100), nullable=False),
    sa.Column('o_email', sa.String(length=120), nullable=False),
    sa.Column('o_phone', sa.String(length=100), nullable=True),
    sa.Column('o_national_id', sa.String(length=100), nullable=True),
    sa.Column('o_lincense_id', sa.String(length=100), nullable=True),
    sa.Column('o_lincense_type', sa.String(length=100), nullable=True),
    sa.Column('o_lincense_expiry', sa.DateTime(), nullable=True),
    sa.Column('o_assigned_asset', sa.Integer(), nullable=True),
    sa.Column('o_payment_card_id', sa.Integer(), nullable=True),
    sa.Column('o_Payment_card_no', sa.String(length=100), nullable=True),
    sa.Column('o_role', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['o_assigned_asset'], ['assets.asset.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('o_email'),
    schema='assets'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('operators', schema='assets')
    # ### end Alembic commands ###
