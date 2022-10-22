from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response, HTTPResponse
from app.models.account_model import Account
from app.models.transaction_model import Transaction

account_bp = Blueprint("account_blueprint")

@account_bp.post('/accounts')
async def create_account(request: Request) -> HTTPResponse:
    session = request.ctx.session
    body = request.json
    async with session.begin():
        account = Account(balance=body['balance'], user_id=body['user_id'])
        session.add_all([account])
    return json_response(account.to_dict(session))

@account_bp.get('/accounts')
async def get_accounts(request: Request) -> HTTPResponse:
    session = request.ctx.session
    accounts = await Account.get_all(session)
    return json_response([await account.to_dict(session) for account in accounts])
    
@account_bp.get('/accounts/<pk:int>')
async def get_account(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    account = await Account.get_by_id(session, pk)
    if not account:
        return HTTPResponse(status=404)
    return json_response(await account.to_dict(session))

@account_bp.delete('/accounts/<pk:int>')
async def delete_account(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    account = await Account.get_by_id(session, pk)
    if not account:
        return HTTPResponse(status=404)
    account_id = account.id
    await session.delete(account)
    await session.commit()
    return json_response({"account_id": account_id})

@account_bp.get('/accounts/<pk:int>/transactions')
async def get_account_transactions(request: Request, pk: int):
    session = request.ctx.session
    if not await Account.get_by_id(session, pk):
        return HTTPResponse(status=404)
    transactions = await Transaction.get_by_account_id(session, pk)
    return json_response([transaction.to_dict() for transaction in transactions])