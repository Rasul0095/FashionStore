from pydantic import BaseModel
from sqlalchemy.ext.asyncio import  AsyncSession
from sqlalchemy import select, insert, update, delete

from src.database import Base

class BaseRepository:
    model = None
    schemas = None
    model: type[Base]
    schemas: type[BaseModel]
    # mapper: DataMapper = None
    # mapper: type[DataMapper]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, *args, **kwargs) -> list[BaseModel]:
        return await self.get_filtered()

    async def get_filtered(self, *filter, **filter_by) -> list[BaseModel]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schemas.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_one_or_none(self, **filter_by) -> BaseModel | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        return self.schemas.model_validate(model, from_attributes=True)

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalar_one()
        return self.schemas.model_validate(model, from_attributes=True)

    async def add(self, data: BaseModel) -> BaseModel | None:
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(stmt)
        model = result.scalars().one()
        return self.schemas.model_validate(model, from_attributes=True)
