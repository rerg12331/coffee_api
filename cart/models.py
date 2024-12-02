from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean, JSON, Text
from models import metadata

Cart = Table(
    "cart",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("product_id", Integer, ForeignKey("product.id")),
    Column("quantity", Integer, nullable=False, default=1),
)