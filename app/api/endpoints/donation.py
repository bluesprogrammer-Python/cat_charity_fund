from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import charityproject_crud, donation_crud
from app.models import User
from app.schemas.donation import AllDonationDB, DonationCreate, UserDonationDB
from app.services.invest import invest_donation

router = APIRouter(prefix='/donation')


@router.post('/',
             response_model=UserDonationDB,
             response_model_exclude_none=True,
             )
async def create_new_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
) -> UserDonationDB:
    """Создание пожертвования. Доступно авторизованным пользователям
    и суперпользователю."""
    new_donation = await donation_crud.create(donation, session, user)
    project_instorage = await charityproject_crud.get_active_objects(session)
    if project_instorage:
        await invest_donation(new_donation, project_instorage, session)
    return new_donation


@router.get(
    '/',
    dependencies=[Depends(current_superuser)],
    response_model=list[AllDonationDB],
    response_model_exclude_none=True,
)
async def get_all_donation(
        session: AsyncSession = Depends(get_async_session),
) -> list[AllDonationDB]:
    """Получение всех пожертвований. Доступно только суперпользователю."""
    all_donation = await donation_crud.read_all_objects_from_db(session)
    return all_donation


@router.get(
    '/my',
    response_model=list[UserDonationDB]
)
async def get_user_donation(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
) -> list[AllDonationDB]:
    """Получение всех пожертвований пользователя отправившего запрос.
    Доступно авторизованным пользователям и суперпользователю"""
    all_user_donation = await donation_crud.read_user_donation(session, user)
    return all_user_donation
