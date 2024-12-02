"""add data in role table

Revision ID: 59273f519949
Revises: db337ad7b4a6
Create Date: 2024-11-30 19:28:58.127940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59273f519949'
down_revision: Union[str, None] = 'db337ad7b4a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("INSERT INTO role (id, name) VALUES (1, 'user');")
    op.execute("INSERT INTO role (id, name) VALUES (2, 'admin');")

def downgrade():
    op.execute("DELETE FROM role WHERE id IN (1, 2);")
