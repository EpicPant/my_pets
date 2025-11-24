"""utils for register and auth user"""

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic import BaseModel
from fastapi import Request, HTTPException, status, Depends
from passlib.context import CryptContext
from app.core.config import auth_settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserDAO
from app.base.session_maker import SessionDep
from loguru import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """hash password func"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_refresh_token(data: dict) -> str:
    """create refresh token"""
    encode_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    encode_data.update({"type": "refresh", "exp": expire})
    refresh_encode = jwt.encode(
        encode_data, auth_settings.SECRET_KEY, auth_settings.ALGORITHM
    )
    return refresh_encode


def create_access_token(data: dict) -> str:
    """create access token func"""
    encode_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    encode_data.update({"type": "access", "exp": expire})
    access_encode = jwt.encode(
        encode_data, auth_settings.SECRET_KEY, auth_settings.ALGORITHM
    )
    return access_encode


def get_access_token(requset: Request):
    token = requset.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token not found"
        )
    return token


async def get_current_user(
    request: Request,
    session: AsyncSession = SessionDep,
):
    token = get_access_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token")

    try:
        payload = jwt.decode(
            token,
            auth_settings.SECRET_KEY,
            algorithms=[auth_settings.ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No sub")

    # если id в БД int:
    user_id = int(user_id)

    user = await UserDAO.find_one_or_none_by_id(id=user_id, session=session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


async def authentificate_user(
    email: BaseModel, plain_password: str, session: AsyncSession
):
    logger.info(
        f"Data for authentification: \nemail:{email},\nplain_password:{plain_password}\n"
    )
    user = await UserDAO.find_user_by_filter(filter=email, session=session)
    logger.info(f"user object:{user}")
    if not user or verify_password(plain_password, user.password) is False:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user doesn't exist",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorect password or email",
        )
    return user
