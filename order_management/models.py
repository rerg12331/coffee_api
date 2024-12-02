from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean, JSON, Text
from models import metadata

Order = Table(
    "order",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("total_price", Integer, nullable=False),
    Column("status", String, default="Ожидает"),
)

OrderItems = Table(
    "order_items",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("order_id", Integer, ForeignKey("order.id")),
    Column("product_id", Integer, ForeignKey("product.id")),
    Column("quantity", Integer, nullable=False),
    Column("price", Integer, nullable=False)
)
