import logging
from sqlalchemy import Column, Integer, Float, ForeignKey, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base
from app.services.account_services import update_balance

logger = logging.getLogger(__name__)
class Transaction(Base):
    __tablename__ = "transaction"
    id = Column("id", Integer(), primary_key=True)
    amount = Column("amount", Float())
    account_id = Column(Integer(), ForeignKey("account.id", ondelete='CASCADE'))
    account = relationship("Account", back_populates="transactions")

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "account_id": self.account_id
        }
    
    @classmethod
    async def get_all(cls, session: AsyncSession) -> list['Transaction']:
        async with session.begin():
            stmt = select(cls)
            result = await session.execute(stmt)
            transactions = result.scalars()
        return transactions
    
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
        session.add_all([self])
        await session.commit()
        await update_balance(session, account_id=self.account_id, amount=self.amount)
        return self