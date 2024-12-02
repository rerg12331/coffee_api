from typing import List, Optional
from fastapi import Query
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: int
    description: str
    category_id: int
    is_available: bool

class ProductCreateResponse(BaseModel):
    status: bool
    new_product: ProductCreate

class Products(BaseModel):
    id: int
    name: str
    price: int
    description: str
    category_id: int
    is_available: bool

class ProductsResponse(BaseModel):
    data: List[Products]

class ProductsDeleteResponse(BaseModel):
    status: bool
    message: str

class ProductsUpdate(BaseModel):
    name: str
    price: int
    description: str
    category_id: int
    is_available: bool    

class ProductsUpdateResponse(BaseModel):
    status: bool
    data: ProductsUpdate

class ProductsUpdatePatch(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_available: Optional[bool] = None
    class Config:
        extra = "ignore"

class ProductsUpdateResponsePatch(BaseModel):
    status: bool
    data: ProductsUpdatePatch

class QueryParams(BaseModel):
    sort_by: Optional[str] = None  # Поле для сортировки
    order: Optional[str] = "asc"  # Порядок сортировки: asc (по возрастанию) или desc (по убыванию)
    search: Optional[str] = None  # Поиск по тексту
    filter: Optional[str] = None
    page: int = 1  # Номер страницы
    page_size: int = 10  # Количество записей на странице
