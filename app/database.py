from contextvars import ContextVar
from sanic import Sanic
from sanic.request import Request
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app import app

bind = create_async_engine("postgresql+asyncpg://postgres:pgsqlpass@db:5432", echo=True)

_sessionmaker = sessionmaker(bind, AsyncSession, expire_on_commit=False)

_base_model_session_ctx = ContextVar("session")

Base = declarative_base()

@app.middleware("request")
async def inject_session(request: Request) -> None:
    request.ctx.session = _sessionmaker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request: Request, response) -> None:
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()