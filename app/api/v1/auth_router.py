"""auth router"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schemas import UserRegister, UserBase
from app.schemas.payment_schemas import CreateWallet
from app.models.user import UserDAO
from app.models.payments import WalletDAO
from app.core.auth import (
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
