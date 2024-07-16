"""adjust firm to organisation

Revision ID: f793d8b3f3b4
Revises: 31e738799860
Create Date: 2024-07-16 11:05:17.756729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f793d8b3f3b4'
down_revision = '31e738799860'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DROP TABLE users.firm CASCADE')
    op.create_table('organization',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('f_name', sa.String(length=80), nullable=False),
    sa.Column('f_industry', sa.String(length=80), nullable=False),
    sa.Column('f_country', sa.String(length=80), nullable=False),
    sa.Column('f_email', sa.String(length=120), nullable=False),
    sa.Column('f_size', sa.Integer(), nullable=False),
    sa.Column('f_fiscal_start', sa.Date(), nullable=True),
    sa.Column('f_fiscal_stop', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('f_country'),
    sa.UniqueConstraint('f_email'),
    sa.UniqueConstraint('f_industry'),
    sa.UniqueConstraint('f_name'),
    schema='users'
    )
    op.execute('DROP TABLE users.users CASCADE')
    op.create_table('users',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('organisation_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username'),
    schema='users'
    )
    op.execute('DROP TABLE assets.assets CASCADE')
    op.create_table('assets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('a_organisation_id', sa.String(), nullable=False),
    sa.Column('a_created_by', sa.String(), nullable=False),
    sa.Column('a_created_at', sa.DateTime(), nullable=False),
    sa.Column('a_name', sa.String(length=100), nullable=False),
    sa.Column('a_make', sa.String(length=100), nullable=False),
    sa.Column('a_model', sa.String(length=100), nullable=False),
    sa.Column('a_year', sa.Integer(), nullable=False),
    sa.Column('a_license_plate', sa.String(length=50), nullable=False),
    sa.Column('a_type', sa.String(length=50), nullable=True),
    sa.Column('a_msrp', sa.Float(), nullable=True),
    sa.Column('a_chasis_no', sa.String(length=100), nullable=True),
    sa.Column('a_engine_size', sa.Float(), nullable=False),
    sa.Column('a_tank_size', sa.Float(), nullable=False),
    sa.Column('a_efficiency_rate', sa.Float(), nullable=False),
    sa.Column('a_fuel_type', sa.String(length=50), nullable=False),
    sa.Column('a_cost', sa.Float(), nullable=False),
    sa.Column('a_value', sa.Float(), nullable=False),
    sa.Column('a_depreciation_rate', sa.Float(), nullable=False),
    sa.Column('a_apreciation_rate', sa.Float(), nullable=False),
    sa.Column('a_accumulated_dep', sa.Float(), nullable=True),
    sa.Column('a_image', sa.String(length=200), nullable=True),
    sa.Column('a_attachment1', sa.String(length=200), nullable=True),
    sa.Column('a_attachment2', sa.String(length=200), nullable=True),
    sa.Column('a_attachment3', sa.String(length=200), nullable=True),
    sa.Column('a_status', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['a_created_by'], ['users.users.id'], ),
    sa.ForeignKeyConstraint(['a_organisation_id'], ['users.organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='assets'
    )
    op.execute('DROP TABLE assets.operators CASCADE')
    op.create_table('operators',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('o_organisation_id', sa.String(), nullable=False),
    sa.Column('o_created_by', sa.String(), nullable=False),
    sa.Column('o_created_at', sa.DateTime(), nullable=False),
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
    sa.Column('o_image', sa.String(length=200), nullable=True),
    sa.Column('o_status', sa.String(length=100), nullable=False),
    sa.Column('o_cum_mileage', sa.Numeric(), nullable=True),
    sa.Column('o_expirence', sa.Numeric(), nullable=True),
    sa.Column('o_attachment1', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['o_assigned_asset'], ['assets.assets.id'], ),
    sa.ForeignKeyConstraint(['o_created_by'], ['users.users.id'], ),
    sa.ForeignKeyConstraint(['o_organisation_id'], ['users.organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('o_email'),
    schema='assets'
    )
    op.execute('DROP TABLE assets.trips CASCADE')
    op.create_table('trips',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('t_created_by', sa.String(), nullable=False),
    sa.Column('t_created_at', sa.DateTime(), nullable=False),
    sa.Column('t_organisation_id', sa.String(), nullable=False),
    sa.Column('t_type', sa.String(length=100), nullable=False),
    sa.Column('t_start_lat', sa.Numeric(), nullable=False),
    sa.Column('t_start_long', sa.Numeric(), nullable=False),
    sa.Column('t_start_elavation', sa.Numeric(), nullable=False),
    sa.Column('t_end_lat', sa.Numeric(), nullable=False),
    sa.Column('t_end_long', sa.Numeric(), nullable=False),
    sa.Column('t_end_elavation', sa.Numeric(), nullable=False),
    sa.Column('t_distance', sa.Float(), nullable=True),
    sa.Column('t_start_date', sa.DateTime(), nullable=True),
    sa.Column('t_end_date', sa.DateTime(), nullable=True),
    sa.Column('t_operator_id', sa.Integer(), nullable=True),
    sa.Column('t_asset_id', sa.Integer(), nullable=True),
    sa.Column('t_status', sa.String(), nullable=False),
    sa.Column('t_load', sa.Float(), nullable=True),
    sa.Column('t_est_fuel', sa.Float(), nullable=True),
    sa.Column('t_actual_fuel', sa.Float(), nullable=True),
    sa.Column('t_est_cost', sa.Float(), nullable=True),
    sa.Column('t_actual_cost', sa.Float(), nullable=True),
    sa.Column('t_consumption_variance', sa.Float(), nullable=True),
    sa.Column('t_cost_variance', sa.Float(), nullable=True),
    sa.Column('t_odometer_reading1', sa.Float(), nullable=True),
    sa.Column('t_dometer_reading2', sa.Float(), nullable=True),
    sa.Column('t_dometer_reading3', sa.Float(), nullable=True),
    sa.Column('t_dometer_reading4', sa.Float(), nullable=True),
    sa.Column('t_dometer_reading5', sa.Float(), nullable=True),
    sa.Column('t_odometer_image1', sa.String(length=200), nullable=True),
    sa.Column('t_odometer_image2', sa.String(length=200), nullable=True),
    sa.Column('t_odometer_image3', sa.String(length=200), nullable=True),
    sa.Column('t_odometer_image4', sa.String(length=200), nullable=True),
    sa.Column('t_odometer_image5', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['t_asset_id'], ['assets.assets.id'], ),
    sa.ForeignKeyConstraint(['t_created_by'], ['users.users.id'], ),
    sa.ForeignKeyConstraint(['t_organisation_id'], ['users.organization.id'], ),
    sa.ForeignKeyConstraint(['t_operator_id'], ['assets.operators.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='assets'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trips', schema='assets')
    op.drop_table('operators', schema='assets')
    op.drop_table('assets', schema='assets')
    op.drop_table('users', schema='users')
    op.drop_table('organization', schema='users')
    # ### end Alembic commands ###