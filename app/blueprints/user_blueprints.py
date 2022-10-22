from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response
from app.models.user_model import User

user_bp = Blueprint("user_blueprint")

@user_bp.post('/users')
async def create_user(request: Request) -> HTTPResponse:
    session = request.ctx.session
    body = request.json
    async with session.begin():
        user = User(username=body['username'], password=body['password'], is_admin=body["is_admin"])
        session.add_all([user])
    return json_response({"user_id": user.id})

@user_bp.get('/users')
async def get_users(request: Request) -> HTTPResponse:
    session = request.ctx.session
    users = await User.get_all(session)
    return json_response([user.to_dict() for user in users])
    
@user_bp.get('/users/<pk:int>')
async def get_user(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    user = await User.get_by_id(session, pk)
    if not user:
        return HTTPResponse(status=404)
    return json_response(user.to_dict())

@user_bp.put('/users/<pk:int>')
async def update_user(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    new_password = request.json.get('password')
    new_is_admin = request.json.get('is_admin')
    user = await User.get_by_id(session, pk)
    if not user:
        return HTTPResponse(status=404)
    if new_password:
        user.password = new_password
    elif new_is_admin is not None:
        user.is_admin = new_is_admin
    await session.commit()
    return json_response(user.to_dict())

@user_bp.delete('/users/<pk:int>')
async def delete_user(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    user = await User.get_by_id(session, pk)
    if not user:
        return HTTPResponse(status=404)
    user_id = user.id
    await session.delete(user)
    await session.commit()
    return json_response({"user_id": user_id})