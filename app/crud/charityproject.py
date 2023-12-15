from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from app.schemas.charityproject import CharityProjectUpdate


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
            self,
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

    async def get_project_by_id(
            self,
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
            self,
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
            self,
            db_project: CharityProject,
            session: AsyncSession,
    ) -> CharityProject:
        """Удаление проекта"""
        await session.delete(db_project)
        await session.commit()
        return db_project

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ):
        """Получение закрытых проектов и сортировка по скорости
        сбора средств"""
        close_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested == True
            )
        )
        close_projects = close_projects.scalars().all()
        sort_projects = sorted(close_projects, key=lambda x: (x.close_date - x.create_date))
        return sort_projects


charityproject_crud = CRUDCharityProject(CharityProject)


"""
for project in close_projects:
            time_diff = project.close_date - project.create_date
            projects_diff_dict[project.id] = time_diff
        sort_data = sorted(projects_diff_dict.items(), key=lambda x: x[1])
"""
