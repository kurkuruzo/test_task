from urllib import request, response
import logging
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response

from app.services.user_services import protected
from app.models.user_model import User
import app.services.user_services as us

logger = logging.getLogger(__name__)

user_bp = Blueprint("user_blueprint")

@user_bp.post("/users/login")
async def do_login(request) -> HTTPResponse:
    response = await us.login_user(request)
    return response

@user_bp.get('/users/activate')
async def activate_user(request: Request) -> HTTPResponse:
    return await us.activate_user(request)
        

@user_bp.post('/users')
async def register_user(request: Request) -> HTTPResponse:
    user_id = await us.create_user(request.ctx.session, request.json)
    return json_response({"activation_link": f"http://127.0.0.1/users/activate?user_id={user_id}"}, status=201)

@user_bp.get('/users')
@protected
async def get_users(request: Request) -> HTTPResponse:
    session = request.ctx.session
    users = await User.get_all(session)
    return json_response([user.to_dict() for user in users])
    
@user_bp.get('/users/<pk:int>')
@protected
async def get_user(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    user = await User.get_by_id(session, pk)
    if not user:
        return HTTPResponse(status=404)
    return json_response(user.to_dict())

@user_bp.put('/users/<pk:int>')
@protected
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
@protected
async def delete_user(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    user = await User.get_by_id(session, pk)
    if not user:
        return HTTPResponse(status=404)
    user_id = user.id
    await session.delete(user)
    await session.commit()
    return json_response({"user_id": user_id})