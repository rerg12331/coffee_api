from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.auth import router as registration_router
from auth.verification import router as verification_router
from auth.jwt_access_refresh import router as jwt_access_refresh_router
from categories_management.crud import router as categories_management_router
from product_management.crud import router as product_management_router
from cart.crud import router as cart_router
from order_management.crud import router as order_management_router
from users_management.crud import router as users_management_router
from fastapi.staticfiles import StaticFiles
import os
from tasks import delete_unverified_users


app = FastAPI(
    title="Coffee",
    version="1.0.0",
    description=""
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(registration_router, prefix="/auth", tags=['Authentication'])
app.include_router(verification_router, prefix="/auth", tags=['Authentication'])
app.include_router(jwt_access_refresh_router, prefix="/auth", tags=['Authentication'])
app.include_router(users_management_router, prefix="/user", tags=['Users-management'])
app.include_router(categories_management_router, prefix="/category", tags=['Categories-management'])
app.include_router(product_management_router, prefix="/product", tags=['Product-management'])
app.include_router(cart_router, prefix="/cart", tags=['Cart'])
app.include_router(order_management_router, prefix="/order", tags=['Order-management'])

@app.on_event("startup")
async def startup_event():
    # Например, можно вызвать задачу при старте приложения
    delete_unverified_users.apply_async()
    print("FastAPI приложение запущено.")


