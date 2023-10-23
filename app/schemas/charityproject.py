from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, validator


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    full_amount: Optional[int] = Field(gt=0)
    description: Optional[str]


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    full_amount: int = Field(gt=0)

    class Config:
        title = 'Схема для создания проекта'


class CharityProjectUpdate(CharityProjectBase):
    @validator('name', 'description', 'full_amount')
    def fields_cannot_be_none(cls, value):
        if value == '':
            raise ValueError('Поля не могут быть пустыми!')
        return value

    class Config:
        extra = Extra.forbid
        title = 'Схема для обновления проекта'


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        title = 'Схема для возвращаемого проекта'
        orm_mode = True
