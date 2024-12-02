from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from auth.schemas import VerificationData, VerificationResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User, Verif_code
from auth.security import check_user
from database import get_db

router = APIRouter()

@router.post("/verification", response_model=VerificationResponse)
async def verification(
    data: VerificationData,
    payload=Depends(check_user),
    db: AsyncSession = Depends(get_db)
):
    async with db.begin():
        result = await db.execute(select(Verif_code).filter(Verif_code.c.user_id == payload['sub']))
        user = result.fetchone()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if data.verification_code == user.code:
            result1 = await db.execute(update(User).where(User.c.id == payload['sub']).values(is_verified=True))
            result2 = await db.execute(delete(Verif_code).where(Verif_code.c.user_id == payload['sub']))

            return VerificationResponse(
                status=True,
                message="User verified successfully"
            )
        else:
            return VerificationResponse(
                status=False,
                message="Invalid verification code"
            )