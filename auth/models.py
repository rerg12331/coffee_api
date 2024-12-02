from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, Boolean, JSON
from models import metadata

Role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)

User = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("role_id", Integer, ForeignKey("role.id")),
    Column("hashed_password", String, nullable=False),
    Column("username", String, nullable=True),
    Column("first_name", String, nullable=True),
    Column("last_name", String, nullable=True),
    Column("phone", String, nullable=True),
    Column("is_verified", Boolean, default=False),
)

Verif_code = Table(
    "verif_code",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("code", Integer, nullable=False),
)