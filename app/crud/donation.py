from datetime import datetime
from typing import Optional
from app.services.invest import invest_donation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.models.donation import Donation
from app.schemas.donation import DonationCreate


async def create_donation(
        new_donation: DonationCreate,
        session: AsyncSession,
        user: Optional[User] = None
) -> Donation:
    new_donation_dict = new_donation.dict()
    if user is not None:
        new_donation_dict['user_id'] = user.id
    new_donation_dict['create_date'] = datetime.now()
    new_donation_dict['close_date'] = None
    new_donation_dict['invested_amount'] = 0
    new_donation_dict['fully_invested'] = False

    """Вызов функции инвестирования"""
    new_donat = await invest_donation(new_donation_dict, session)

    db_donation = Donation(**new_donat)
    session.add(db_donation)
    await session.commit()
    await session.refresh(db_donation)
    return db_donation


async def read_all_donations_from_db(
        session: AsyncSession,
) -> list[Donation]:
    db_donation = await session.execute(select(Donation))
    return db_donation.scalars().all()


async def read_user_donation(
        session: AsyncSession,
        user: Optional[User] = None
) -> list[Donation]:
    db_user_donation = await session.execute(
        select(Donation).where(
            Donation.user_id == user.id
        )
    )
    db_user_donation = db_user_donation.scalars().all()
    return db_user_donation
