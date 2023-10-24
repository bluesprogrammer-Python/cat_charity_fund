from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


async def invest_donation(
        new_object: Union[CharityProject, Donation],
        invest_lst: Union[list[CharityProject], list[Donation]],
        session: AsyncSession
) -> None:
    """Функция инвестирования новых пожертвований в существующие проекты или
    инвестирования новых проектов существующими пожертвованиями."""
    full_amount: int = new_object.full_amount
    for invest in invest_lst:
        balance = full_amount - (invest.full_amount - invest.invested_amount)
        if balance < 0:
            new_object.fully_invested = True
            new_object.close_date = datetime.now()
            new_object.invested_amount = invest.full_amount
            invest.invested_amount += full_amount
        elif full_amount - (invest.full_amount - invest.invested_amount) > 0:
            invest.fully_invested = True
            invest.close_date = datetime.now()
            invest.invested_amount = invest.full_amount
            new_object.invested_amount += full_amount - balance
            full_amount = balance
        else:
            invest.fully_invested = True
            invest.close_date = datetime.now()
            invest.invested_amount = invest.full_amount
            new_object.fully_invested = True
            new_object.close_date = datetime.now()
            new_object.invested_amount = invest.full_amount
        session.add(invest)

        if balance <= 0:
            break

    session.add(new_object)
    await session.commit()
    await session.refresh(new_object)
