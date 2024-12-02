from fastapi import APIRouter, Depends, HTTPException, status
from auth.jwt_handler import create_access_token, create_refresh_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth.models import User
from auth.schemas import AccessResponse, RefreshResponse
from database import get_db
from config import SECRET, ALGORITHM
import jwt

router = APIRouter()

SECRET_KEY = SECRET 

@router.post("/access", response_model=AccessResponse)
async def access(refresh_token: str, db: AsyncSession = Depends(get_db)) -> AccessResponse:
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Проверяем, существует ли пользователь
        result = await db.execute(select(User).filter(User.c.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        access_token = await create_access_token({"sub": user_id})

        return AccessResponse(access_token=access_token, token_type="bearer")
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)) -> RefreshResponse:
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Проверяем пользователя
        result = await db.execute(select(User).filter(User.c.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        new_access_token = await create_access_token({"sub": user_id})
        new_refresh_token = await create_refresh_token({"sub": user_id})

        return RefreshResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
