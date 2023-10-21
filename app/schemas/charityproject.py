from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    full_amount: Optional[int] = Field(gt=0)
    description: Optional[str]
    invested_amount: int = Field(default=0)
    fully_invested: bool = False


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    full_amount: int = Field(gt=0)

    class Config:
        title = 'Схема для создания проекта'


# Схема для полученных данных.
class CharityProjectUpdate(CharityProjectBase):

    @validator('name')
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError('Имя проекта не может быть пустым!')
        return value


    class Config:
        title = 'Схема для обновления проекта'


# Схема для возвращаемого объекта.
class CharityProjectDB(CharityProjectCreate):
    id: int

    class Config:
        title = 'Схема для возвращаемого объекта'
        orm_mode = True
