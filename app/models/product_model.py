from typing import Any
from sqlalchemy import Column, Integer, String, Float, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base

class Product(Base):
    __tablename__ = "product"
    id = Column("id", Integer(), primary_key=True)
    title = Column("title", String(length=200))
    description = Column("description", Text())
    price = Column("price", Float(), default=0.0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price
        }
    
    @classmethod
    async def get_all(cls, session: AsyncSession):
        async with session.begin():
            stmt = select(cls)
            result = await session.execute(stmt)
            products = result.scalars()
        return products
    
    @classmethod
    async def get_by_id(cls, session, id) -> 'Product':
        async with session.begin():
            return await session.get(cls, id)
        
    async def save(self, session) -> 'Product':
        async with session.begin():
            await session.flush()
            return self