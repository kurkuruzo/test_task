import asyncio
from contextvars import ContextVar
import logging
from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from models import User, Base


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

app = Sanic('app')

bind = create_async_engine("postgresql+asyncpg://postgres:pgsqlpass@localhost:5432", echo=True)

_sessionmaker = sessionmaker(bind, AsyncSession, expire_on_commit=False)

_base_model_session_ctx = ContextVar("session")

@app.middleware("request")
async def inject_session(request):
    request.ctx.session = _sessionmaker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


@app.get('/test')
async def test(request: Request)-> HTTPResponse:
    return json_response({"result": "Working fine"}) 


@app.post('/users')
async def create_user(request: Request) -> HTTPResponse:
    session = request.ctx.session
    body = request.json
    async with session.begin():
        user = User(username=body['username'], password=body['password'], is_admin=body["is_admin"])
        session.add_all([user])
    return json_response({"user_id": user.id})

@app.get('/users')
async def get_users(request: Request) -> HTTPResponse:
    session = request.ctx.session
    users = await User.get_all(session)
    return json_response([user.to_dict() for user in users])
    
@app.get('/users/<pk:int>')
async def get_user(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    user = await User.get_user_by_id(session, pk)
    return json_response(user.to_dict())

@app.put('/users/<pk:int>')
async def update_user(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    new_password = request.json.get('password')
    new_is_admin = request.json.get('is_admin')
    user = await User.get_user_by_id(session, pk)
    if new_password:
        user.password = new_password
    elif new_is_admin is not None:
        user.is_admin = new_is_admin
    await session.commit()
    return json_response(user.to_dict())

@app.delete('/users/<pk:int>')
async def delete_user(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    user = await User.get_user_by_id(session, pk)
    user_id = user.id
    await session.delete(user)
    await session.commit()
    return json_response({"user_id": user_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234, dev=True)