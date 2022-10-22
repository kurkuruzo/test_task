from typing import Any
from sqlalchemy import Column, Integer, String, Float, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload
from app.database import Base

class Account(Base):
    __tablename__ = "account"
    id = Column("id", Integer(), primary_key=True)
    balance = Column("balance", Float(), default=0.0)
    user_id = Column(Integer(), ForeignKey("user.id", ondelete='CASCADE'))
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

    async def to_dict(self, session):
        res = await session.execute(select(Account).options(selectinload(Account.transactions)))
        return {
            "id": self.id,
            "balance": self.balance,
            "transactions": [transaction.to_dict() for transaction in self.transactions],
            "user_id": self.user_id
        }
    
    @classmethod
    async def get_all(cls, session: AsyncSession):
        async with session.begin():
            stmt = select(cls)
            result = await session.execute(stmt)
            products = result.scalars()
        return products
    
    @classmethod
    async def get_by_id(cls, session, id) -> 'Account':
        async with session.begin():
            return await session.get(cls, id)
        
    async def save(self, session) -> 'Account':
        async with session.begin():
            await session.flush()
            return self