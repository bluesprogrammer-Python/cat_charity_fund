from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import get_project_by_id, get_project_id_by_name
from app.schemas.charityproject import CharityProjectDB, CharityProjectUpdate


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProjectDB:
    """Проверка наличия проекта в БД по его id"""
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
        project: CharityProjectDB,
) -> None:
    """Проверка состояния проекта в БД - закрыт или нет"""
    if project.close_date is not None:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return project


async def check_project_is_invest(
        project: CharityProjectDB,
) -> None:
    """Проверка наличия вложенных инвестиций в проект"""
    if project.invested_amount != 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!',
        )
    return project


async def check_project_fullamount(
        project: CharityProjectDB,
        obj_in: CharityProjectUpdate,
) -> None:
    """Проверка статуса и суммы проекта перед обновлением"""
    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )
    if (obj_in.full_amount and
       obj_in.full_amount < project.invested_amount):
        raise HTTPException(
            status_code=422,
            detail='Требуемая сумма не может быть меньше уже внесенной!'
        )
    if (obj_in.full_amount and
       obj_in.full_amount == project.invested_amount):
        project.fully_invested = True
        project.close_date = datetime.now()


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    """Проверка имени на уникальность перед созданием нового проекта"""
    project_id = await get_project_id_by_name(project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_desc_exists(
        project_description: str,
) -> None:
    """Проверка отправки пустых значений перед обновлением для поля description"""
    if project_description is None or project_description == "":
        raise HTTPException(
            status_code=422,
            detail='Создание проектов с пустым описанием запрещено.',
        )
