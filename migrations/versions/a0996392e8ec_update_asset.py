"""update asset

Revision ID: a0996392e8ec
Revises: 60eae5b7a5e6
Create Date: 2025-02-20 12:11:07.758045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0996392e8ec'
down_revision = '60eae5b7a5e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assets', schema='assets') as batch_op:
        batch_op.alter_column('a_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('a_engine_size',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('a_tank_size',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('a_efficiency_rate',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('a_cost',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('a_value',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('a_depreciation_rate',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('a_apreciation_rate',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assets', schema='assets') as batch_op:
        batch_op.alter_column('a_apreciation_rate',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
        batch_op.alter_column('a_depreciation_rate',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
        batch_op.alter_column('a_value',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
        batch_op.alter_column('a_cost',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
        batch_op.alter_column('a_efficiency_rate',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
        batch_op.alter_column('a_tank_size',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
        batch_op.alter_column('a_engine_size',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
        batch_op.alter_column('a_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)

    # ### end Alembic commands ###
