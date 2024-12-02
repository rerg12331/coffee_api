import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import and_, asc, delete, desc, or_, select, update
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import check_admin, check_user
from users_management.schemas import *
from auth.models import *
from cart.models import *
from order_management.models import *
from database import get_db

router = APIRouter()

@router.post("/me", response_model=UserInfo)
async def me(
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
) -> UserInfo:
    user_id = payload["sub"]

    # Получение данных пользователя
    user_stmt = select(User).where(User.c.id == user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получение данных корзины
    cart_stmt = select(Cart.c.product_id, Cart.c.quantity).where(Cart.c.user_id == user_id)
    cart_result = await db.execute(cart_stmt)
    cart_items = cart_result.fetchall()

    # Получение данных заказов
    orders_stmt = select(Order.c.id, Order.c.total_price, Order.c.status).where(Order.c.user_id == user_id)
    orders_result = await db.execute(orders_stmt)
    order_items = orders_result.fetchall()

    return UserInfo(
        email=user.email,
        role_id=user.role_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        is_verified=user.is_verified,
        cart=[
            {"product_id": item.product_id, "quantity": item.quantity} for item in cart_items
        ],
        orders=[
            {"id": order.id, "total_price": order.total_price, "status": order.status} for order in order_items
        ]
    )

@router.get("/users", response_model=list[UserBaseInfo])
async def get_users(
    payload=Depends(check_admin),
    query_params: QueryParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(User)
    
    # Фильтры
    if query_params.filter:
        try:
            filters_dict = json.loads(query_params.filter)
            filters = [
                getattr(User.c, field) == value
                for field, value in filters_dict.items()
                if hasattr(User.c, field)
            ]
            if filters:
                query = query.where(and_(*filters))
        except json.JSONDecodeError:
            return JSONResponse(content={"detail": "Invalid filter format. Please provide a valid JSON string."}, status_code=400)

    # Поиск
    if query_params.search:
        search_filter = or_(
            User.c.username.ilike(f"%{query_params.search}%"),
            User.c.first_name.ilike(f"%{query_params.search}%"),
            User.c.last_name.ilike(f"%{query_params.search}%"),
            User.c.email.ilike(f"%{query_params.search}%"),
            User.c.phone.ilike(f"%{query_params.search}%")
        )
        query = query.where(search_filter)

    # Сортировка
    if query_params.sort_by and hasattr(User.c, query_params.sort_by):
        order_by_column = getattr(User.c, query_params.sort_by)
        query = query.order_by(asc(order_by_column) if query_params.order == "asc" else desc(order_by_column))
    
    # Пагинация
    offset = (query_params.page - 1) * query_params.page_size
    query = query.offset(offset).limit(query_params.page_size)

    result = await db.execute(query)
    users = result.fetchall()

    return [
        UserBaseInfo(
            id=user.id,
            email=user.email,
            role_id=user.role_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            is_verified=user.is_verified,
        )
        for user in users
    ]

@router.get("/user/{id}", response_model=UserInfo)
async def get_user(
    id: int, 
    payload=Depends(check_admin),
    db: AsyncSession = Depends(get_db)
):
    # Получение данных пользователя
    user_stmt = select(User).where(User.c.id == id)
    user_result = await db.execute(user_stmt)
    user = user_result.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получение данных корзины
    cart_stmt = select(Cart.c.product_id, Cart.c.quantity).where(Cart.c.user_id == id)
    cart_result = await db.execute(cart_stmt)
    cart_items = cart_result.fetchall()

    # Получение данных заказов
    orders_stmt = select(Order.c.id, Order.c.total_price, Order.c.status).where(Order.c.user_id == id)
    orders_result = await db.execute(orders_stmt)
    order_items = orders_result.fetchall()

    return UserInfo(
        email=user.email,
        role_id=user.role_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        is_verified=user.is_verified,
        cart=[
            {"product_id": item.product_id, "quantity": item.quantity} for item in cart_items
        ],
        orders=[
            {"id": order.id, "total_price": order.total_price, "status": order.status} for order in order_items
        ]
    )

@router.put("/user/{id}", response_model=UserResponse)
async def update_user(
    id: int, 
    user_data: UserInfoUpdatePut, 
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            result = await db.execute(select(User).where(User.c.id == id))
            user = result.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            update_data = user_data.dict()
            await db.execute(User.update().where(User.c.id == id).values(update_data))

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not update user"
        )
    
    return UserResponse(status=True, update_data=update_data)

@router.patch("/user/{id}", response_model=UserResponse)
async def update_user(
    id: int, 
    user_data: UserInfoUpdatePut, 
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            result = await db.execute(select(User).where(User.c.id == id))
            user = result.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            update_data = {
                key: value for key, value in user_data.dict(exclude_unset=True).items()
            }

            if not update_data:
                raise HTTPException(
                    status_code=400,
                    detail="No fields to update"
                )
            
            await db.execute(User.update().where(User.c.id == id).values(update_data))

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not update user"
        )
    
    return UserResponse(status=True, update_data=update_data)


@router.delete("/user/{id}", response_model=DeleteUserResponse)
async def delete_user(
    id: int, 
    payload=Depends(check_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            result = await db.execute(select(User).where(User.c.id == id))
            user = result.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            order_query = await db.execute(select(Order).where(Order.c.user_id == id))
            oreder_id = order_query.fetchone()
            if oreder_id:
                await db.execute(OrderItems.delete().where(OrderItems.c.order_id == oreder_id.id))
            await db.execute(Order.delete().where(Order.c.user_id == id))
            await db.execute(Cart.delete().where(Cart.c.user_id == id))
            await db.execute(User.delete().where(User.c.id == id))

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not delete user"
        )
    return DeleteUserResponse(status=True, message="User deleted")