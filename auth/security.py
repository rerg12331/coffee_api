from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from auth.jwt_handler import verify_token
from auth.models import User
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()

async def check_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = await verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

async def check_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = await verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).filter(User.c.id == payload['sub']))
    info_user_data = result.fetchone()
    if info_user_data.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Not an admin",
        )

    return info_user_data