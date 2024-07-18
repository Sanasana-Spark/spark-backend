"""adjust timefield in operators

Revision ID: 97a2ec218032
Revises: 356eaa06befb
Create Date: 2024-07-18 00:40:47.111901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97a2ec218032'
down_revision = '356eaa06befb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('operators', schema='assets') as batch_op:
        batch_op.alter_column('o_created_at',
                                existing_type=sa.DateTime(),
                                server_default=sa.text('now()'),
                                nullable=False)
        # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('operators', schema='assets')
    # ### end Alembic commands ###
