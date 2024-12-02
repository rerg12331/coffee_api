import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import and_, asc, delete, desc, or_, select, update
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import check_admin
from product_management.schemas import ProductCreate, ProductCreateResponse, Products, ProductsDeleteResponse, ProductsResponse, ProductsUpdate, ProductsUpdatePatch, ProductsUpdateResponse, ProductsUpdateResponsePatch, QueryParams
from product_management.unit import get_product_by_id
from database import get_db
from product_management.models import Product
from categories_management.models import Category

router = APIRouter()

@router.post("/product", response_model=ProductCreateResponse)
async def add_product(
    data: ProductCreate,
    payload=Depends(check_admin),
    db: AsyncSession = Depends(get_db)
) -> ProductCreateResponse:
    
    try:
        async with db.begin():
            new_product = data.dict()
            await db.execute(
                Product.insert().values(new_product)
            )
    except Exception as e:
            print(f"Error occurred: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: Could not add new product"
            )

    return ProductCreateResponse(
        status=True,
        new_product=new_product
    )

@router.get("/products", response_model=ProductsResponse)
async def products(
    query_params: QueryParams = Depends(),
    db: AsyncSession = Depends(get_db)
) -> ProductsResponse:
    query = select(Product)
    
    # Фильтры
    if query_params.filter:
        try:
            filters_dict = json.loads(query_params.filter)
            filters = [
                getattr(Product.c, field) == value
                for field, value in filters_dict.items()
                if hasattr(Product.c, field)
            ]
            if filters:
                query = query.where(and_(*filters))
        except json.JSONDecodeError:
            return JSONResponse(content={"detail": "Invalid filter format. Please provide a valid JSON string."}, status_code=400)

    # Поиск
    if query_params.search:
        search_filter = or_(
            Product.c.name.ilike(f"%{query_params.search}%"),
            Product.c.description.ilike(f"%{query_params.search}%")
        )
        query = query.where(search_filter)

    # Сортировка
    if query_params.sort_by and hasattr(Product.c, query_params.sort_by):
        order_by_column = getattr(Product.c, query_params.sort_by)
        query = query.order_by(asc(order_by_column) if query_params.order == "asc" else desc(order_by_column))
    
    # Пагинация
    offset = (query_params.page - 1) * query_params.page_size
    query = query.offset(offset).limit(query_params.page_size)
    
    # Выполнение запроса
    result = await db.execute(query)
    products_list = [
        {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'category_id': product.category_id,
            'is_available': product.is_available
        }
        for product in result.fetchall()
    ]
    
    return ProductsResponse(data=products_list)

@router.get("/product/{id}", response_model=Products)
async def product(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Products:
    
    product = await get_product_by_id(id, db)

    return Products(id=product.id, 
                    name=product.name, 
                    price=product.price, 
                    description=product.description, 
                    category_id=product.category_id, 
                    is_available=product.is_available)

@router.put("/product/{id}", response_model=ProductsUpdateResponse)
async def update_product_put(
    id: int,
    data: ProductsUpdate,
    db: AsyncSession = Depends(get_db),
    payload=Depends(check_admin), 
) -> ProductsUpdateResponse:
    
    try:
        async with db.begin():
            product = await get_product_by_id(id, db)

            put_product = data.dict()
            query = await db.execute(select(Category).where(Category.c.id == put_product["category_id"]))

            if not query.fetchone():
                raise HTTPException(status_code=404, detail=f"Category with id {put_product['category_id']} not found")

            await db.execute(Product.update().where(Product.c.id == id).values(put_product))

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
            print(f"Error occurred: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: Could not update product"
            )
    
    return ProductsUpdateResponse(status=True, data=put_product)

@router.patch("/product/{id}", response_model=ProductsUpdateResponsePatch)
async def update_product_patch(
    id: int,
    data: ProductsUpdatePatch,
    db: AsyncSession = Depends(get_db),
    payload=Depends(check_admin),
) -> ProductsUpdateResponsePatch:
    
    try:
        async with db.begin():
            update_data = {
                key: value for key, value in data.dict(exclude_unset=True).items()
            }

            if not update_data:
                raise HTTPException(
                    status_code=400,
                    detail="No fields to update"
                )
            
            product = await get_product_by_id(id, db)

            if "category_id" in update_data:
                query = await db.execute(select(Category).where(Category.c.id == update_data["category_id"]))
                if not query.fetchone():
                    raise HTTPException(status_code=404, detail=f"Category with id {update_data['category_id']} not found")
                    
            await db.execute(Product.update().where(Product.c.id == id).values(update_data))

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
            print(f"Error occurred: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: Could not update product"
            )    
    return ProductsUpdateResponsePatch(status=True, data=update_data)

@router.delete("/product/{id}", response_model=ProductsDeleteResponse)
async def delete_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    payload=Depends(check_admin),
) -> ProductsDeleteResponse:
    
    try:
        async with db.begin():
            product = await get_product_by_id(id, db)
            await db.execute(delete(Product).where(Product.c.id == id))

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
            print(f"Error occurred: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error: Could not delete product"
            )

    return ProductsDeleteResponse(
        status=True,
        message="Product deleted"
    )