"""adjust organization field from f_ to org_

Revision ID: ac34c940cc0d
Revises: d24e60cb7035
Create Date: 2024-07-16 11:47:17.517468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac34c940cc0d'
down_revision = 'd24e60cb7035'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DROP TABLE users.organization CASCADE')
    op.create_table('organization',
    sa.Column('id', sa.String(), nullable=True),
    sa.Column('default_id', sa.Integer(), nullable=False),
    sa.Column('org_name', sa.String(length=80), nullable=False),
    sa.Column('org_industry', sa.String(length=80), nullable=True),
    sa.Column('org_country', sa.String(length=80), nullable=True),
    sa.Column('org_email', sa.String(length=120), nullable=True),
    sa.Column('org_size', sa.Integer(), nullable=True),
    sa.Column('org_fiscal_start', sa.Date(), nullable=True),
    sa.Column('org_fiscal_stop', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('default_id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('org_name'),
    schema='users'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('organization', schema='users')
    # ### end Alembic commands ###
