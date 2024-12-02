import json
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import and_, asc, delete, desc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import check_admin, check_user
from order_management.send_email import send_email
from order_management.schemas import OrderCreateResponse, OrderResponse, OrderUpdatePatch, OrderUpdatePut, Orders, OrdersDeleteResponse, OrdersResponse, QueryParams
from database import get_db
from product_management.models import Product
from order_management.models import Order, OrderItems
from cart.models import Cart
from auth.models import *

router = APIRouter()

@router.post("/order", response_model=OrderCreateResponse)
async def create_order(
    background_tasks: BackgroundTasks,
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload["sub"]
    try:
        async with db.begin():
            # Получаем товары из корзины пользователя
            result = await db.execute(
                select(Cart, Product)
                .join(Product, Product.c.id == Cart.c.product_id)
                .where(Cart.c.user_id == user_id, Product.c.is_available == True)
            )
            cart_items = result.fetchall()

            if not cart_items:
                raise HTTPException(status_code=400, detail="Cart is empty or products unavailable")
            
            total_price = sum(item.price * item.quantity for item in cart_items)
            new_order = {
                "user_id": user_id, 
                "total_price": total_price, 
                "status": "Ожидает"
                }

            result = await db.execute(Order.insert().returning(Order.c.id).values(new_order))
            order_id = result.scalar_one()

            # Добавляем товары в таблицу OrderItems
            for item in cart_items:
                order_item = {
                    "order_id": order_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price
                }
                await db.execute(OrderItems.insert().values(order_item))

            # Удаляем товары из корзины
            await db.execute(delete(Cart).where(Cart.c.user_id == user_id))
            
            admin = await db.execute(select(User).where(User.c.role_id == 2))
            admin_mail = admin.fetchone()

            background_tasks.add_task(send_email, recipient_email=admin_mail.email, body=f"{new_order}")

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Error when placing an order")

    return OrderCreateResponse(status=True, new_order=new_order)


@router.get("/orders", response_model=Orders)
async def get_orders(
    query_params: QueryParams = Depends(),
    payload=Depends(check_admin),
    db: AsyncSession = Depends(get_db)
) -> Orders:
    
    query = select(Order) 

    # Фильтры
    if query_params.filter:
        try:
            filters_dict = json.loads(query_params.filter) 
            filters = [
                getattr(Order.c, field) == value 
                for field, value in filters_dict.items()
                if hasattr(Order.c, field) 
            ]
            if filters:
                query = query.where(and_(*filters)) 
        except json.JSONDecodeError:
            return JSONResponse(content={"detail": "Invalid filter format. Please provide a valid JSON string."}, status_code=400)

    # Поиск
    if query_params.search:
        search_filter = (
            Order.c.status.ilike(f"%{query_params.search}%")
        )
        query = query.where(search_filter)

    if query_params.total_price:
        total_price_filter = (
            Order.c.total_price == int(query_params.total_price) 
        )
        query = query.where(total_price_filter)

    # Сортировка
    if query_params.sort_by and hasattr(Order.c, query_params.sort_by):
        order_by_column = getattr(Order.c, query_params.sort_by)
        query = query.order_by(asc(order_by_column) if query_params.order == "asc" else desc(order_by_column))
    
    # Пагинация
    offset = (query_params.page - 1) * query_params.page_size
    query = query.offset(offset).limit(query_params.page_size)

    # Выполнение запроса
    result = await db.execute(query)
    orders = result.fetchall()

    if not orders:
        return Orders(data=[])
    
    return Orders(
        data=[{
            "id": order.id,
            "total_price": order.total_price,
            "status": order.status
        } for order in orders]
    )


@router.get("/order/{id}", response_model=OrderResponse)
async def get_order(
    id: int,
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload["sub"]

    order_stmt = select(Order).where(Order.c.id == id, Order.c.user_id == user_id)
    result = await db.execute(order_stmt)
    order = result.fetchone()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order {id} not found")

    items_stmt = select(OrderItems, Product).join(Product, Product.c.id == OrderItems.c.product_id).where(OrderItems.c.order_id == id)
    items_result = await db.execute(items_stmt)
    items = items_result.fetchall()

    print(items)

    return OrderResponse(
        id=order.id,
        total_price=order.total_price,
        status=order.status,
        items=[
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": item.price
            }   for item in items
        ])


@router.put("/order/{id}", response_model=OrdersResponse)
async def update_order_put(
    id: int,
    data: OrderUpdatePut,
    payload=Depends(check_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            order_query = await db.execute(select(Order).where(Order.c.id == id))
            order = order_query.scalar_one_or_none()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            await db.execute(
                Order.update().where(Order.c.id == id).values(total_price=data.total_price, status=data.status)
            )

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Error when updating the order")
    
    except HTTPException as http_exc:
        raise http_exc
    
    return OrdersResponse(
            id=id,
            total_price=data.total_price,
            status=data.status,
        )


@router.patch("/order/{id}", response_model=OrdersResponse)
async def update_order_patch(
    id: int,
    data: OrderUpdatePatch,
    payload=Depends(check_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            order_query = await db.execute(select(Order).where(Order.c.id == id))
            order = order_query.scalar_one_or_none()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            update_data = {
                key: value for key, value in data.dict(exclude_unset=True).items()
            }

            await db.execute(
                Order.update().where(Order.c.id == id).values(update_data)
            )

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Error when updating the order")
    
    return OrdersResponse(
            id=id,
            total_price=data.total_price,
            status=data.status,
        )

@router.delete("/order/{id}", response_model=OrdersDeleteResponse)
async def delete_order(
    id: int,
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload["sub"]
    
    try:
        async with db.begin():
            order_query = await db.execute(select(Order).where(Order.c.id == id, Order.c.user_id == user_id))
            order = order_query.scalar_one_or_none()

            if not order:
                raise HTTPException(status_code=404, detail=f"Order {id} not found or unauthorized")
            
            stmt = await db.execute(delete(OrderItems).where(OrderItems.c.order_id == id))

            stmt = await db.execute(delete(Order).where(Order.c.id == id))

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Error deleting order")

    return OrdersDeleteResponse(status=True, message=f"Order {id} deleted successfully")

