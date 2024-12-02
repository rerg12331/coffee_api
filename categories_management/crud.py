import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import and_, asc, delete, desc, func, or_, select, update
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import check_admin
from categories_management.schemas import Categories, CategoriesDeleteResponse, CategoriesResponse, CategoriesUpdate, CategoriesUpdatePatch, CategoriesUpdateResponse, CategoriesUpdateResponsePatch, CategoryCreate, CategoryCreateResponse, QueryParams
from categories_management.unit import get_category_by_id
from database import get_db
from categories_management.models import Category
from product_management.models import Product

router = APIRouter()

@router.post("/category", response_model=CategoryCreateResponse)
async def add_category(
    data: CategoryCreate,
    payload=Depends(check_admin),
    db: AsyncSession = Depends(get_db)
) -> CategoryCreateResponse:
    
    try:
        async with db.begin():
            new_category = data.dict()

            await db.execute(
                Category.insert().values(new_category)
            )
    except Exception as e:
            print(f"Error occurred: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: Could not add new category"
            )

    return CategoryCreateResponse(
        status=True,
        new_category=new_category
    )

@router.get("/categories", response_model=CategoriesResponse)
async def categories(
    query_params: QueryParams = Depends(),
    db: AsyncSession = Depends(get_db)
) -> CategoriesResponse:
    query = select(Category)
    
    # Фильтры
    if query_params.filter:
        try:
            filters_dict = json.loads(query_params.filter)
            filters = [
                getattr(Category.c, field) == value
                for field, value in filters_dict.items()
                if hasattr(Category.c, field)
            ]
            if filters:
                query = query.where(and_(*filters))
        except json.JSONDecodeError:
            return JSONResponse(content={"detail": "Invalid filter format. Please provide a valid JSON string."}, status_code=400)

    
    # Поиск
    if query_params.search:
        search_filter = or_(
            func.lower(Category.c.name).ilike(f"%{query_params.search.lower()}%"),
            func.lower(Category.c.description).ilike(f"%{query_params.search.lower()}%")
        )
        query = query.where(search_filter)
    
    # Сортировка
    if query_params.sort_by and hasattr(Category.c, query_params.sort_by):
        order_by_column = getattr(Category.c, query_params.sort_by)
        query = query.order_by(asc(order_by_column) if query_params.order == "asc" else desc(order_by_column))
    
    # Пагинация
    offset = (query_params.page - 1) * query_params.page_size
    query = query.offset(offset).limit(query_params.page_size)

    result = await db.execute(query)
    categories_list = [
        {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'is_active': category.is_active
        } 
        for category in result.fetchall()
    ]
    
    return CategoriesResponse(data=categories_list)

@router.get("/category/{id}", response_model=Categories)
async def category(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Categories:
    category = await get_category_by_id(id, db)

    return Categories(id=category.id, name=category.name, description=category.description, is_active=category.is_active)

@router.put("/category/{id}", response_model=CategoriesUpdateResponse)
async def update_category_put(
    id: int,
    data: CategoriesUpdate,
    db: AsyncSession = Depends(get_db),
    payload=Depends(check_admin), 
) -> CategoriesUpdateResponse:
    
    try:
        async with db.begin():
            category = await get_category_by_id(id, db)

            put_category = data.dict()
            
            await db.execute(
                Category.update().where(Category.c.id == id).values(put_category)
            )
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not update category"
        )

    return CategoriesUpdateResponse(status=True, data=put_category)


@router.patch("/category/{id}", response_model=CategoriesUpdateResponsePatch)
async def update_category_patch(
    id: int,
    data: CategoriesUpdatePatch,
    db: AsyncSession = Depends(get_db),
    payload=Depends(check_admin),

) -> CategoriesUpdateResponsePatch:
    
    try:
        async with db.begin():
            update_data = {
                key: value for key, value in data.dict(exclude_unset=True).items()
            }

            # Если нет полей для обновления, бросаем исключение
            if not update_data:
                raise HTTPException(
                    status_code=400,
                    detail="No fields to update"
                )
            
            category = await get_category_by_id(id, db)
            
            await db.execute(
                Category.update().where(Category.c.id == id).values(update_data)
            )
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not update category"
        )        

    return CategoriesUpdateResponsePatch(status=True, data=update_data)

@router.delete("/category/{id}", response_model=CategoriesDeleteResponse)
async def delete_category(
    id: int,
    db: AsyncSession = Depends(get_db),
    payload=Depends(check_admin),
) -> CategoriesDeleteResponse:
    
    try:
        async with db.begin():
            category = await get_category_by_id(id, db)
            await db.execute(delete(Product).where(Product.c.category_id == id))
            await db.execute(delete(Category).where(Category.c.id == id))
            
    except HTTPException as http_exc:
        raise http_exc
            
    except Exception as e:
            print(f"Error occurred: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: Could not delete category"
            )        

    return CategoriesDeleteResponse(
        status=True,
        message="Category deleted"
    )