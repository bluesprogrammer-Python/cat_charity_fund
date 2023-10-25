from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User
from app.models.donation import Donation


class CRUDDonation(CRUDBase):

    async def read_user_donation(
            self,
            session: AsyncSession,
            user: Optional[User] = None
    ) -> list[Donation]:
        """Получение всех пожертвований определенного пользователя"""
        db_user_donation = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        db_user_donation = db_user_donation.scalars().all()
        return db_user_donation


donation_crud = CRUDDonation(Donation)
