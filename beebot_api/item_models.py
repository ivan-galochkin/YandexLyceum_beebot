from typing import Optional
from pydantic import BaseModel


class UserItem(BaseModel):
    telegram_id: Optional[int]
    table: Optional[str]
