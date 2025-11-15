import uuid
from pydantic import BaseModel


class CreateWallet(BaseModel):
    id: uuid.UUID
    user_id: int
    balance: int = 0
