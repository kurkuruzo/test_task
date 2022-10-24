from urllib import request
from venv import create
import jwt
import logging
from sanic import Blueprint, text
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response
from sanic.exceptions import Forbidden, BadRequest, NotFound

from app.services.user_services import protected
from app.models.user_model import User
from app.services.user_services import check_password, create_user

logger = logging.getLogger(__name__)

user_bp = Blueprint("user_blueprint")

@user_bp.post("/users/login")
async def do_login(request) -> HTTPResponse:
    session = request.ctx.session
    if not request.json.get('username') or not request.json.get("password"):
        raise BadRequest("Please provide username and password")
    user_to_authenticate = await User.get_by_username(session, request.json['username'])
    is_password_match = check_password(user_to_authenticate, request.json["password"])
    if is_password_match:
        token = jwt.encode({}, request.app.config.SECRET)
        return text(token)
    raise Forbidden("Username or password is not correct")

@user_bp.get('/users/activate')
async def activate_user(request: Request) -> HTTPResponse:
    user_id = request.query_args["user_id"]
    user = await User.get_by_id(request.ctx.session, user_id)
    if user:
        user.is_active = True
        return json_response({"user_id": user.id, "user_is_active": user.is_active})
    return NotFound("User not found")
        

@user_bp.post('/users')
async def register_user(request: Request) -> HTTPResponse:
    user_id = await create_user(request.ctx.session, request.json)
    return json_response({"activation_link": f"http://127.0.0.1/users/activate?user_id={user_id}"})

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