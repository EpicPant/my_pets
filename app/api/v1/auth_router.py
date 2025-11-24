"""auth router"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Response
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schemas import (
    UserRegister,
    UserBase,
    UserLogin,
    EmailModel,
    UserInfo,
)
from app.schemas.payment_schemas import CreateWallet
from app.models.user import UserDAO, User
from app.models.payments import WalletDAO
from app.core.auth import (
    authentificate_user,
    get_current_user,
    get_access_token,
    create_access_token,
    create_refresh_token,
)
from app.base.session_maker import TransactionDep

auth_router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@auth_router.post("/register")
async def register(
    request_data: UserRegister, session: AsyncSession = Depends(TransactionDep)
):
    """register router"""
    logger.info(f"Recived data: {request_data}")
    data_to_db = UserBase(
        **request_data.model_dump(exclude={"confirm_password"}).copy()
    )
    try:
        user = await UserDAO.add(data_to_db, session)
    except IntegrityError as e:
        await session.rollback()
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    wallet_uuid = uuid.uuid4()
    wallet_add = CreateWallet(id=wallet_uuid, user_id=user.id)
    await WalletDAO.add(data=wallet_add, session=session)

    return {"register_data": request_data}


@auth_router.post("/login")
async def login(
    response: Response,
    user_data: UserLogin,
    session: AsyncSession = Depends(TransactionDep),
):
    """login endpoint"""
    logger.info(f"Recived data for login: {user_data}")
    check = await authentificate_user(
        email=EmailModel(email=user_data.email),
        plain_password=user_data.password,
        session=session,
    )

    access_token = create_access_token(data={"sub": str(check.id)})
    refresh_token = create_refresh_token(data={"sub": str(check.id)})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 60 * 24 * 60,
    )

    return {
        "ok": True,
        "message": "nice login!",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@auth_router.post("/logout")
async def logout(response: Response):
    """logout endpoint"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@auth_router.post("/me")
async def get_me(user_data: User = Depends(get_current_user)) -> UserInfo:
    """get user data endpoint"""
    logger.info(user_data)
    return UserInfo.model_validate(user_data)
