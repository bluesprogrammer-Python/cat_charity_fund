from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import (create_charityproject, delete_project,
                                     get_project_by_id, get_project_id_by_name,
                                     read_all_projects_from_db, update_project)
from app.schemas.charityproject import (CharityProjectCreate, CharityProjectDB,
                                        CharityProjectUpdate)

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
    await check_name_duplicate(charityproject.name, session)
    await check_desc_exists(charityproject.description, session)
    new_project = await create_charityproject(charityproject, session)
    return new_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
        session: AsyncSession = Depends(get_async_session),
):
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
    project = await check_project_exists(
        project_id, session
    )
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    project = await update_project(
        project, obj_in, session
    )
    return project


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await get_project_id_by_name(project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_desc_exists(
        project_description: str,
        session: AsyncSession,
) -> None:
    if project_description is None or project_description == "":
        raise HTTPException(
            status_code=422,
            detail='Создание проектов с пустым описанием запрещено.',
        )


@router.delete(
    '/{project_id}',
    dependencies=[Depends(current_superuser)],
    response_model=CharityProjectDB,
)
async def remove_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    project = await check_project_exists(
        project_id, session
    )
    project = await check_project_close(
        project_id, session
    )
    project = await delete_project(
        project, session
    )
    return project


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProjectDB:
    project = await get_project_by_id(
        project_id, session
    )
    if project is None:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return project


async def check_project_close(
        project_id: int,
        session: AsyncSession,
) -> CharityProjectDB:
    project = await get_project_by_id(
        project_id, session
    )
    if project.close_date is not None:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return project
