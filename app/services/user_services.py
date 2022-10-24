from functools import wraps
from hashlib import sha256
import jwt

from sanic import text, Request
from app.models.user_model import User


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
            # is_active = check_user_is_active(request)
            
            if is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            # elif is_authenticated:
            #     return text(f"User is not active. Please activate using the activation link", 401)
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

def check_password(user: User, password: str) -> bool:
    return user.password_hash == make_hash(str(password))

def make_hash(value) -> str:
    return sha256(value.encode()).hexdigest()

def check_user_is_active(request):
    pass