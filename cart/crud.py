from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from auth.security import check_user
from cart.models import Cart
from product_management.models import Product
from cart.schemas import CartAdd, CartItemResponse, DeleteItemResponse
from database import get_db

router = APIRouter()

@router.post("/cart", response_model=CartItemResponse)
async def add_to_cart(
    data: CartAdd,
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
) -> CartItemResponse:
    
    try:
        async with db.begin():
            stmt = select(Product).where(Product.c.id == data.product_id, Product.c.is_available == True)
            result = await db.execute(stmt)
            product = result.fetchone()

            if not product:
                raise HTTPException(status_code=404, detail="Product not found or unavailable")

            new_product = data.dict()
            new_product["user_id"] = payload['sub']
            await db.execute(
                Cart.insert().values(new_product)
            )
            
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not add item to cart"
        )

    return CartItemResponse(
        status=True,
        message="Item added to cart successfully",
        item=data
    )


@router.delete("/cart/{id}")
async def delete_item_from_cart(
    id: int,
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
) -> DeleteItemResponse:
    try:
        async with db.begin():
            stmt = await db.execute(delete(Cart).where(Cart.c.id == id and Cart.c.user_id == payload['sub']))
            if stmt.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item with id {id} not found"
                )
            
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not delete item from cart"
        )

    return DeleteItemResponse(status=True, message=f"Item with id {id} deleted")


@router.delete("/cart")
async def clear_cart(
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
) -> DeleteItemResponse:
    try:
        async with db.begin():
            stmt = await db.execute(delete(Cart).where(Cart.c.user_id == payload['sub']))

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not clear cart"
        )
    
    return DeleteItemResponse(status=True, message="All items in cart deleted")