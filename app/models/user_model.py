from typing import Any
from sqlalchemy import Column, Integer, String, Boolean, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from hashlib import sha256
from app.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column("id", Integer(), primary_key=True, autoincrement=True)
    username = Column("username", String(length=50), unique=True)
    password_hash = Column("password_hash", String(length=500))
    is_admin = Column("is_admin", Boolean(), default=False)
    is_active = Column("is_active", Boolean(), default=False)
    accounts = relationship("Account", back_populates="user")
    
    def __init__(self, username: str, password: str, is_admin: bool=False, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.is_admin = is_admin
    
    @property
    def password(self):
        pass
    
    @password.setter
    def password(self, value):
        self.password_hash = sha256(str(value).encode()).hexdigest()
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
            "is_admin": self.is_admin
        }
    
    @classmethod
    async def get_all(cls, session: AsyncSession):
        async with session.begin():
            stmt = select(cls)
            result = await session.execute(stmt)
            users = result.scalars()
        return users
    
    @classmethod
    async def get_by_id(cls, session, id) -> 'User':
        async with session.begin():
            return await session.get(cls, id)
        
    @classmethod
    async def get_by_username(cls, session: AsyncSession, username: str) -> 'User':
        async with session.begin():
            stmt = select(cls).where(cls.username == username)
            result = await session.execute(stmt)
            user = result.scalar()
            return user
        
    async def save(self, session) -> 'User':
        async with session.begin():
            await session.flush()
            return self