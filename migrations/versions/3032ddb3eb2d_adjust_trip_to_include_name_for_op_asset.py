"""adjust trip to include name for op & asset

Revision ID: 3032ddb3eb2d
Revises: f08b7d7ee7b0
Create Date: 2024-07-21 15:13:45.879171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3032ddb3eb2d'
down_revision = 'f08b7d7ee7b0'
branch_labels = None
depends_on = None


def upgrade():
    return 0

