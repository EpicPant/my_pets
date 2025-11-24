from typing import Generic, TypeVar
from sqlalchemy import select, update, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.base.database import Base
from pydantic import BaseModel
from loguru import logger

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    """Base class for DAO classes"""

    model: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session
        if self.model is None:
            raise ValueError("в дочернем классе должна быть указанна модель")

    @classmethod
    async def find_one_or_none_by_id(cls, id, session: AsyncSession):
        """find by id"""
        logger.info(f"Find {cls.model.__name__} with id {id}")
        try:
            query = select(cls.model).filter_by(id=id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Find record with ID {id}")
            else:
                logger.info(f"Record with ID {id} not found.")
            return record
        except Exception as e:
            logger.error(f"Error in find_one_or_none_by_id: {e}")
            raise

    @classmethod
    async def find_all_by_filter(cls, filter: BaseModel, session: AsyncSession):
        """find by filter"""
        logger.info(f"Find {cls.model.__name__} by {filter.__class__.__name__}")
        filter_dict = filter.model_dump(exclude_unset=True)
        print(filter_dict)
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalars().all()
            if record:
                logger.info(f"Find record {cls.model.__name__}")
            else:
                logger.info(f"Record not found by filter {filter}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Error in find_all_by_filter: {e}")
            raise

    @classmethod
    async def add(cls, data: BaseModel, session: AsyncSession):
        logger.info(f"Recived Data: {data}")
        instance = data.model_dump()
        new_instance = cls.model(**instance)
        session.add(new_instance)
        try:
            await session.flush()
            logger.info(f"data add to {cls.model.__name__}")
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Can't add data to {cls.model.__name__} error:{e}")
            raise
