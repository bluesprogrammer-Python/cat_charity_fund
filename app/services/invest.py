from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation

STORAGE_FOND = []


async def invest_donation(
        new_donation_dict,
        session: AsyncSession,
):
    """Функция распределения денег по проектам"""
    EXTRA_INVESTED = 0
    IS_IN_STORAGE = False
    donation = new_donation_dict['full_amount']
    project = await session.execute(
        select(CharityProject).order_by(
            CharityProject.create_date
        ).where(CharityProject.fully_invested == 0)
    )
    project = project.scalars().first()
    """Проверка на наличие открытых проектов. Если они отсутствуют, то вся
    сумма пожертвования переходит в список STORAGE_FOND"""
    if project is not None:
        """Проверка на недобор суммы инвестирования в проект"""
        if donation + project.invested_amount < project.full_amount:
            """Установка значения для модели CharityProject"""
            project.invested_amount += donation
            """Установка значения для модели Donation"""
            new_donation_dict['close_date'] = datetime.now()
            new_donation_dict['invested_amount'] += donation
            new_donation_dict['fully_invested'] = True

        elif donation + project.invested_amount == project.full_amount:
            """Установка значений для модели CharityProject"""
            project.invested_amount += donation
            project.fully_invested = True
            project.close_date = datetime.now()
            """Установка значения для модели Donation"""
            new_donation_dict['close_date'] = datetime.now()
            new_donation_dict['invested_amount'] += donation
            new_donation_dict['fully_invested'] = True

        elif donation + project.invested_amount > project.full_amount:
            EXTRA_INVESTED = (donation + project.invested_amount) - project.full_amount
            INVESTED_BEFORE = project.invested_amount
            """Установка значений для модели CharityProject"""
            project.invested_amount = project.full_amount
            project.fully_invested = True
            project.close_date = datetime.now()
            """Установка значения для модели Donation"""
            new_donation_dict['invested_amount'] += (project.full_amount - INVESTED_BEFORE)
    else:
        STORAGE_FOND.append(donation)
    """Запуск цикла инвестирования оставшихся средств в другие открытые проекты.
    При отсутствии открытых проектов все не распределенные средства остаются
    на балансе в списке STORAGE_FOND"""
    while EXTRA_INVESTED != 0 and IS_IN_STORAGE is False:
        ANSWERS = await extra_invest(EXTRA_INVESTED, new_donation_dict, session)
        if len(ANSWERS) == 1:
            new_donation_dict = ANSWERS[0]
            IS_IN_STORAGE = False
            EXTRA_INVESTED = 0
        elif len(ANSWERS) == 2:
            new_donation_dict = ANSWERS[0]
            EXTRA_INVESTED = ANSWERS[1]
        else:
            new_donation_dict = ANSWERS[0]
            IS_IN_STORAGE = ANSWERS[1]
            EXTRA_INVESTED = ANSWERS[2]
    print(STORAGE_FOND)
    return new_donation_dict


async def extra_invest(EXTRA_INVESTED, new_donation_dict, session: AsyncSession):
    """Функция для дополнительного инвестирования в другие открытые проекты"""
    project = await session.execute(
        select(CharityProject).order_by(
            CharityProject.create_date
        ).where(CharityProject.fully_invested == 0)
    )
    project = project.scalars().first()
    if project is not None:
        if EXTRA_INVESTED + project.invested_amount < project.full_amount:
            """Установка значения для модели CharityProject"""
            project.invested_amount += EXTRA_INVESTED
            """Установка значения для модели Donation"""
            new_donation_dict['close_date'] = datetime.now()
            new_donation_dict['invested_amount'] += EXTRA_INVESTED
            new_donation_dict['fully_invested'] = True
            return [new_donation_dict]

        elif EXTRA_INVESTED + project.invested_amount == project.full_amount:
            """Установка значений для модели CharityProject"""
            project.invested_amount += EXTRA_INVESTED
            project.fully_invested = True
            project.close_date = datetime.now()
            """Установка значения для модели Donation"""
            new_donation_dict['close_date'] = datetime.now()
            new_donation_dict['invested_amount'] += EXTRA_INVESTED
            new_donation_dict['fully_invested'] = True
            return [new_donation_dict]

        elif EXTRA_INVESTED + project.invested_amount > project.full_amount:
            EXTRA_INVESTED = (EXTRA_INVESTED + project.invested_amount) - project.full_amount
            INVESTED_BEFORE = project.invested_amount
            """Установка значений для модели CharityProject"""
            project.invested_amount = project.full_amount
            project.fully_invested = True
            project.close_date = datetime.now()
            """Установка значения для модели Donation"""
            new_donation_dict['invested_amount'] += (project.full_amount - INVESTED_BEFORE)
            return [new_donation_dict, EXTRA_INVESTED]
    else:
        IS_IN_STORAGE = True
        STORAGE_FOND.append(EXTRA_INVESTED)
        return [new_donation_dict, IS_IN_STORAGE, EXTRA_INVESTED]


async def invest_extra_in_new_project(
        new_project_dict,
        session: AsyncSession):
    donation = await session.execute(
        select(Donation).order_by(
            Donation.create_date
        ).where(Donation.fully_invested == 0)
    )
    donation = donation.scalars().first()
    if len(STORAGE_FOND) > 0:
        rezerv_donation = STORAGE_FOND[0]
        if rezerv_donation < new_project_dict['full_amount']:
            """Установка значения для модели CharityProject"""
            new_project_dict['invested_amount'] += rezerv_donation
            donation.invested_amount += rezerv_donation
            donation.fully_invested = True
            donation.close_date = datetime.now()
            del STORAGE_FOND[0]

        elif rezerv_donation == new_project_dict['full_amount']:
            """Установка значений для модели CharityProject"""
            new_project_dict['invested_amount'] += rezerv_donation
            new_project_dict['close_date'] = datetime.now()
            new_project_dict['fully_invested'] = True
            donation.invested_amount += rezerv_donation
            donation.fully_invested = True
            donation.close_date = datetime.now()
            del STORAGE_FOND[0]

        elif rezerv_donation > new_project_dict['full_amount']:
            EXTRA_INVESTED = rezerv_donation - new_project_dict['full_amount']
            """Установка значений для модели CharityProject"""
            new_project_dict['invested_amount'] += new_project_dict['full_amount']
            new_project_dict['close_date'] = datetime.now()
            new_project_dict['fully_invested'] = True
            donation.invested_amount += new_project_dict['full_amount']
            STORAGE_FOND[0] = EXTRA_INVESTED

    print(STORAGE_FOND)
    return new_project_dict
