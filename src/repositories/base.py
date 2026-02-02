import logging
from pydantic import BaseModel
from asyncpg import UniqueViolationError
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import  AsyncSession
from sqlalchemy import select, insert, update, delete

from src.database import Base
from src.exceptions.exception import ObjectNotFoundException, ObjectAlreadyExistsHTTPException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    model: type[Base]
    mapper: DataMapper = None
    mapper: type[DataMapper]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, *args, **kwargs) -> list[BaseModel]:
        return await self.get_filtered()

    async def get_filtered(self, *filter, **filter_by) -> list[BaseModel]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_one_or_none(self, **filter_by) -> BaseModel | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel) -> BaseModel | None:
        try:
            stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            logging.exception(f"Не удалось добавить данные БД, входные данные={data}")
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExistsHTTPException
            else:
                logging.exception(f"Незнакомая ошибка: не удалось добавить данные БД, входные данные={data}")
                raise ex

    async def add_bulk(self, data: [BaseModel]):
        add_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_stmt)

    async def exit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(stmt)

    async def delete(self, *filter, **filter_by):
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)
