from typing import Any, Union
from sqlalchemy import Column, Integer, Float, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base
from app.models.account_model import Account

class Transaction(Base):
    __tablename__ = "transaction"
    id = Column("id", Integer(), primary_key=True)
    amount = Column("amount", Float(), unique=True)
    account_id = Column(Integer(), ForeignKey("account.id", ondelete='CASCADE'))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "account_id": self.account_id
        }
    
    @classmethod
    async def get_all(cls, session: AsyncSession):
        async with session.begin():
            stmt = select(cls)
            result = await session.execute(stmt)
            products = result.scalars()
        return products
    
    @classmethod
    async def get_by_id(cls, session, id) -> 'Transaction':
        async with session.begin():
            return await session.get(cls, id)
        
    @classmethod
    async def get_by_account_id(cls, session, account_id) -> 'Transaction':
        async with session.begin():
            stmt = select(cls).filter(cls.account_id == account_id)
            res = await session.execute(stmt)
            return res.scalars().all()
        
    async def save(self, session) -> 'Transaction':
        async with session.begin():
            await session.flush()
            return self