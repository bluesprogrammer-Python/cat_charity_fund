from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.schemas.charityproject import (CharityProjectCreate,
                                        CharityProjectUpdate)


async def create_charityproject(
        new_project: CharityProjectCreate,
        session: AsyncSession
) -> CharityProject:
    """Создание записи в БД с новым проектом"""
    new_project_dict = new_project.dict()
    new_project_dict['create_date'] = datetime.now()
    new_project_dict['close_date'] = None
    new_project_dict['invested_amount'] = 0
    new_project_dict['fully_invested'] = False

    db_project = CharityProject(**new_project_dict)
    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)
    return db_project


async def get_project_id_by_name(
        project_name: str,
        session: AsyncSession
) -> Optional[int]:
    """Получение id проекта из БД по имени проета"""
    db_project_id = await session.execute(
        select(CharityProject.id).where(
            CharityProject.name == project_name
        )
    )
    db_project_id = db_project_id.scalars().first()
    return db_project_id


async def read_all_projects_from_db(
        session: AsyncSession,
) -> list[CharityProject]:
    """Получение всех проектов из БД"""
    db_projects = await session.execute(select(CharityProject))
    return db_projects.scalars().all()


async def get_project_by_id(
        project_id: int,
        session: AsyncSession,
) -> Optional[CharityProject]:
    """Получение определенного проекта по id"""
    db_project = await session.execute(
        select(CharityProject).where(
            CharityProject.id == project_id
        )
    )
    db_project = db_project.scalars().first()
    return db_project


async def update_project(
        db_project: CharityProject,
        project_in: CharityProjectUpdate,
        session: AsyncSession,
) -> CharityProject:
    """Обновление проекта"""
    obj_data = jsonable_encoder(db_project)
    update_data = project_in.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_project, field, update_data[field])
    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)
    return db_project


async def delete_project(
        db_project: CharityProject,
        session: AsyncSession,
) -> CharityProject:
    """Удаление проекта"""
    await session.delete(db_project)
    await session.commit()
    return db_project


async def get_active_projects(
        session: AsyncSession
) -> list[CharityProject]:
    """Получение не закрытых проектов из БД для инвестирования"""
    project_instorage = await session.execute(
        select(CharityProject).where(
            CharityProject.fully_invested == false()).order_by(
                CharityProject.id)
    )
    return project_instorage.scalars().all()
