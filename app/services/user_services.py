from datetime import datetime, timedelta
from functools import wraps
from hashlib import sha256
import jwt
import logging

from sanic import text, json, Request
from sanic.exceptions import NotFound, BadRequest
from app.models.user_model import User

logger = logging.getLogger(__name__)

def check_token(request):
    if not request.token:
        return False

    try:
        jwt.decode(
            request.token, request.app.config.SECRET, algorithms=["HS256"]
        )
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True


def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated = check_token(request)
            
            if is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text("You are unauthorized.", 401)

        return decorated_function

    return decorator(wrapped)

async def create_user(session, request_body) -> str:
    async with session.begin():
        user = User(username=request_body['username'], password=request_body['password'], is_admin=request_body["is_admin"])
        session.add(user)
        await session.commit()
        return user.id
    
async def login_user(request: Request):
    session = request.ctx.session
    if not request.json.get('username') or not request.json.get("password"):
        raise BadRequest("Please provide username and password")
    user_to_authenticate = await User.get_by_username(session, request.json['username'])
    is_password_match = check_password(user_to_authenticate, request.json["password"])
    if not user_to_authenticate.is_active:
        return text(f"User is not active. Please activate using the activation link: {_make_link(user_to_authenticate.id)}", 401)
    if is_password_match : 
        token = jwt.encode({'user': user_to_authenticate.id, "exp": datetime.utcnow() + timedelta(minutes=10)}, request.app.config.SECRET)
        return json({"token": token})
    raise NotFound("User not found")

async def activate_user(request: Request):
    user_id = int(request.args['user_id'][0])
    user = await User.get_by_id(request.ctx.session, user_id)
    session = request.ctx.session
    if user:
        user.is_active = True
        session.add(user)
        await session.commit()
        return json({"user_id": user.id, "user_is_active": user.is_active})
    raise NotFound("User not found")

def check_password(user: User, password: str) -> bool:
    return user.password_hash == make_hash(str(password))

def make_hash(value) -> str:
    return sha256(value.encode()).hexdigest()

def _make_link(user_id: int) -> str:
    return f"127.0.0.1:1234/users/activate?user_id={user_id}"
