from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(email: str, password: str, db: AsyncSession) -> dict:
    query = select(User).where(User.c.email == email)
    result = await db.execute(query)
    user_record = result.first()

    if user_record:
        if verify_password(password, user_record.hashed_password):
            return {'id': user_record.id}
    return None
