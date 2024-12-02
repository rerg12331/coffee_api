from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from categories_management.models import Category


async def get_category_by_id(id: int, db: AsyncSession):
    result = await db.execute(select(Category).where(Category.c.id == id))
    category = result.fetchone()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category