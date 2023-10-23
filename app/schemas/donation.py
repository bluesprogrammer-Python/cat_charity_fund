from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DonationBase(BaseModel):
    comment: Optional[str]


class DonationCreate(DonationBase):
    full_amount: int = Field(gt=0)

    class Config:
        title = 'Схема для создания пожертвования'


class UserDonationDB(DonationCreate):
    id: int
    full_amount: int
    create_date: datetime

    class Config:
        title = 'Схема для получения информации о пожертвовании'
        orm_mode = True


class AllDonationDB(DonationCreate):
    id: int
    create_date: datetime
    user_id: int
    invested_amount: int = Field(default=0)
    fully_invested: bool = Field(default=False)
    close_date: datetime = Field(default=None)

    class Config:
        title = 'Схема для получения информации обо всех пожертвованиях'
        orm_mode = True
