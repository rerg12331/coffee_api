from typing import List, Optional
from fastapi import Query
from pydantic import BaseModel



class Orderinfo(BaseModel):
    user_id: int
    total_price: int
    status: str

class OrderCreateResponse(BaseModel):
    status: bool
    new_order: Orderinfo

class OrdersResponse(BaseModel):
    id: Optional[int]
    total_price: Optional[int]
    status: Optional[str]

class Orders(BaseModel):
    data: List[OrdersResponse] 

class OrderItems(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: int

class OrderResponse(BaseModel):
    id: int
    total_price: int
    status: str  
    items: List[OrderItems]

class OrderUpdatePut(BaseModel):
    total_price: int
    status: str

class OrderUpdatePatch(BaseModel):
    total_price: Optional[int] = None
    status: Optional[str] = None
    class Config:
        extra = "ignore"


class OrdersDeleteResponse(BaseModel):
    status: bool
    message: str

class QueryParams(BaseModel):
    sort_by: Optional[str] = None  # Поле для сортировки
    order: Optional[str] = "asc"  # Порядок сортировки: asc (по возрастанию) или desc (по убыванию)
    search: Optional[str] = None  # Поиск по тексту
    total_price: Optional[int] = None  # Поиск по тексту
    filter: Optional[str] = Query(None, description="Фильтры в формате JSON, например: {'field1': 'value1', 'field2': 'value2'}")  # Фильтры как строка
    page: int = 1  # Номер страницы
    page_size: int = 10  # Количество записей на странице