from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, Boolean, JSON, Text
from models import metadata

Category = Table(
    "category",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", Text, nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
)