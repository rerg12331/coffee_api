from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean, JSON, Text
from models import metadata

Product = Table(
    "product",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("price", Integer, nullable=True),
    Column("category_id", Integer, ForeignKey("category.id")),
    Column("description", Text, nullable=True),
    Column("is_available", Boolean, nullable=False, default=True),
)