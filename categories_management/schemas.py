from typing import Dict, List, Optional
from fastapi import Query
from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str
    description: str
    is_active: bool

class CategoryCreateResponse(BaseModel):
    status: bool
    new_category: CategoryCreate

class Categories(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool

class CategoriesResponse(BaseModel):
    data: List[Categories]

class CategoriesUpdate(BaseModel):
    name: str
    description: str
    is_active: bool

class CategoriesUpdatePatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    class Config:
        extra = "ignore"

class CategoriesUpdateResponse(BaseModel):
    status: bool
    data: CategoriesUpdate

class CategoriesUpdateResponsePatch(BaseModel):
    status: bool
    data: CategoriesUpdatePatch

class CategoriesDeleteResponse(BaseModel):
    status: bool
    message: str

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float

class QueryParams(BaseModel):
    sort_by: Optional[str] = None  # Поле для сортировки
    order: Optional[str] = "asc"  # Порядок сортировки: asc (по возрастанию) или desc (по убыванию)
    search: Optional[str] = None  # Поиск по тексту
    filter: Optional[str] = None
    page: int = 1  # Номер страницы
    page_size: int = 10  # Количество записей на странице