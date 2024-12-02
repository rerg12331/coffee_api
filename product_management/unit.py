from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from product_management.models import Product


async def get_product_by_id(id: int, db: AsyncSession):
    result = await db.execute(select(Product).where(Product.c.id == id))
    product = result.fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product