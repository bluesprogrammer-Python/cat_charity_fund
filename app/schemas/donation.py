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
    user_id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        title = 'Схема для получения информации обо всех пожертвованиях'
        orm_mode = True
