"""add defoult admin in User

Revision ID: c1295f08b587
Revises: 4dd48a1999ae
Create Date: 2024-12-02 18:22:51.491031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1295f08b587'
down_revision: Union[str, None] = '4dd48a1999ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Вставка данных в таблицу (предположим, что таблица называется "users")
    op.execute("""
        INSERT INTO public."user" (id, email, role_id, hashed_password, username, first_name, last_name, phone, is_verified)
        VALUES
        (1, 'user@example.com', 2, '$2b$12$P63Ak3qY3Eu29jimSKUdO.wb85MX1R.OVxgXHz1ZfXZg4XXvS9GlK', 'admin', 'ADMIN', 'ADMIN_ADMIN', null, true);
    """)

def downgrade() -> None:
    # Откат вставленных данных (удаление вставленных строк)
    op.execute("""
        DELETE FROM public."user" WHERE id = 1;
    """)