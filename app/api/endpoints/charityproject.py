from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_desc_exists, check_name_duplicate,
                                check_project_close, check_project_exists,
                                check_project_fullamount,
                                check_project_is_invest)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import (create_charityproject, delete_project,
                                     read_all_projects_from_db, update_project)
from app.crud.donation import get_active_donation
from app.schemas.charityproject import (CharityProjectCreate, CharityProjectDB,
                                        CharityProjectUpdate)
from app.services.invest import invest_donation

router = APIRouter(prefix='/charity_project')


@router.post(
    '/',
    dependencies=[Depends(current_superuser)],
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def create_new_project(
        charityproject: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Создание проекта. Доступно только для суперпользователя."""
    await check_name_duplicate(charityproject.name, session)
    await check_desc_exists(charityproject.description)
    new_project = await create_charityproject(charityproject, session)
    donation_instorage = await get_active_donation(session)
    if donation_instorage:
        await invest_donation(new_project, donation_instorage, session)
    return new_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """Получение всех проектов. Доступно всем, даже неавторизованным
    пользователям."""
    all_projects = await read_all_projects_from_db(session)
    return all_projects


@router.patch(
    '/{project_id}',
    dependencies=[Depends(current_superuser)],
    response_model=CharityProjectDB,
)
async def partially_update_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Обновление проекта по id. Доступно только для суперпользователя."""
    project = await check_project_exists(
        project_id, session
    )
    await check_project_fullamount(project, obj_in)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    project = await update_project(
        project, obj_in, session
    )
    return project


@router.delete(
    '/{project_id}',
    dependencies=[Depends(current_superuser)],
    response_model=CharityProjectDB,
)
async def remove_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Удаление проекта по id. Доступно только для суперпользователя."""
    project = await check_project_exists(
        project_id, session
    )
    project_check_close = await check_project_close(
        project
    )
    project_check_invest = await check_project_is_invest(
        project_check_close
    )
    del_project = await delete_project(
        project_check_invest, session
    )
    return del_project
