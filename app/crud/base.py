from typing import Optional, Union

from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.charity_project import CharityProject
from app.models.donation import Donation


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def read_all_objects_from_db(
            self,
            session: AsyncSession
    ) -> Optional[Union[list[CharityProject], list[Donation]]]:
        """Получение всех объектов модели из БД"""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
            self,
            obj_in,
            session: AsyncSession,
            user: Optional[User] = None
    ) -> Optional[Union[CharityProject, Donation]]:
        """Создание объектов модели в БД"""
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_active_objects(
            self,
            session: AsyncSession
    ) -> Optional[Union[list[CharityProject], list[Donation]]]:
        """Получение не закрытых объектов из БД для инвестирования"""
        active_objs = await session.execute(
            select(self.model).where(
                self.model.fully_invested == false()).order_by(
                    self.model.id)
        )
        return active_objs.scalars().all()
