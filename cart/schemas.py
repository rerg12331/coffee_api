from typing import List, Optional
from pydantic import BaseModel, Field

class CartAdd(BaseModel):
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., gt=0, description="Количество товаров")

class CartItemResponse(BaseModel):
    status: bool
    message: str
    item: CartAdd

class DeleteItemResponse(BaseModel):
    status: bool
    message: str