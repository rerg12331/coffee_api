from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from auth.send_email import send_email
from auth.jwt_handler import create_access_token, create_refresh_token
from auth.unit import authenticate_user, get_password_hash
from auth.schemas import AuthenticationResponse, AuthenticationUserLogin, RegistrationUserCreate, RegistrationResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert
from auth.models import User, Verif_code
from database import get_db
import random

router = APIRouter()

@router.post("/registration", response_model=RegistrationResponse)
async def registration(user: RegistrationUserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)) -> RegistrationResponse:
    try:
        async with db.begin():
            result_user = await db.execute(select(User).filter(User.c.email == user.email))
            existing_user = result_user.scalars().first()

            if existing_user:  # Проверка на существующего пользователя
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            hashed_password = get_password_hash(user.password)

            new_user = {
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "hashed_password": hashed_password,
                "role_id": 1
            }

            result = await db.execute(
                insert(User).values(new_user).returning(User.c.id)
            )

            user_id = result.scalar_one()

            verif_number = random.randint(100000, 999999)

            result = await db.execute(Verif_code.insert().values(user_id=user_id, code=verif_number))

            background_tasks.add_task(send_email, recipient_email=user.email, code=verif_number)

    except Exception as e:
        print(f"Error occurred: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not register user"
        )

    return RegistrationResponse(
        message="User registered successfully",
        user_id= user_id
    )


@router.post("/authentication", response_model=AuthenticationResponse)
async def authentication(user: AuthenticationUserLogin, db: AsyncSession = Depends(get_db)) -> AuthenticationResponse:
    authenticated_user = await authenticate_user(user.email, user.password, db)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await create_access_token({"sub": authenticated_user["id"]})
    refresh_token = await create_refresh_token({"sub": authenticated_user["id"]})
    
    return AuthenticationResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )