from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response
from app import app
from app.models.user_model import User

@app.get('/test')
async def test(request: Request)-> HTTPResponse:
    return json_response({"result": "Working fine"}) 


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234, dev=True)
    