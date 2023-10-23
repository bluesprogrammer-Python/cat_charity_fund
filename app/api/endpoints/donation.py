from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import (create_donation, read_all_donations_from_db,
                               read_user_donation)
from app.models import User
from app.schemas.donation import AllDonationDB, DonationCreate, UserDonationDB

router = APIRouter(prefix='/donation')


@router.post('/',
             response_model=UserDonationDB,
             response_model_exclude_none=True,
             )
async def create_new_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    new_donation = await create_donation(donation, session, user)
    return new_donation


@router.get(
    '/',
    dependencies=[Depends(current_superuser)],
    response_model=list[AllDonationDB],
)
async def get_all_donation(
        session: AsyncSession = Depends(get_async_session),
):
    all_donation = await read_all_donations_from_db(session)
    return all_donation


@router.get(
    '/my',
    response_model=list[UserDonationDB]
)
async def get_user_donation(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    all_user_donation = await read_user_donation(session, user)
    return all_user_donation
