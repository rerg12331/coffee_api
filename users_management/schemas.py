from typing import List, Optional
from pydantic import BaseModel

class CartItem(BaseModel):
    product_id: int
    quantity: int

class OrderItem(BaseModel):
    id: int
    total_price: int
    status: str

class UserBaseInfo(BaseModel):
    id: int
    email: str
    role_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    is_verified: bool

class UserInfo(BaseModel):
    email: str
    role_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    is_verified: bool
    cart: List[CartItem]
    orders: List[OrderItem]

class DeleteUserResponse(BaseModel):
    status: bool
    message: str

class UserInfoUpdatePut(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    class Config:
        extra = "ignore"

class UserResponse(BaseModel):
    status: bool
    update_data: UserInfoUpdatePut

class QueryParams(BaseModel):
    sort_by: Optional[str] = None  # Поле для сортировки
    order: Optional[str] = "asc"  # Порядок сортировки: asc (по возрастанию) или desc (по убыванию)
    search: Optional[str] = None  # Поиск по тексту
    filter: Optional[str] = None  # Фильтры как строка в формате JSON
    page: int = 1  # Номер страницы
    page_size: int = 10  # Количество записей на странице