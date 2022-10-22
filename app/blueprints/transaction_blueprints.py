from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response
from app.models.transaction_model import Transaction

transaction_bp = Blueprint("transaction_blueprint")

@transaction_bp.post('/transactions')
async def create_transaction(request: Request) -> HTTPResponse:
    session = request.ctx.session
    body = request.json
    async with session.begin():
        transaction = Transaction(account_id=body['account_id'], amount=body['amount'])
        session.add_all([transaction])
    return json_response(transaction.to_dict())

@transaction_bp.get('/transactions')
async def get_transactions(request: Request) -> HTTPResponse:
    session = request.ctx.session
    transactions = await Transaction.get_all(session)
    return json_response([transaction.to_dict() for transaction in transactions])
    
@transaction_bp.get('/transactions/<pk:int>')
async def get_transaction(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    transaction = await Transaction.get_by_id(session, pk)
    return json_response(transaction.to_dict())

@transaction_bp.delete('/transactions/<pk:int>')
async def delete_transaction(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    transaction = await Transaction.get_by_id(session, pk)
    transaction_id = transaction.id
    await session.delete(transaction)
    await session.commit()
    return json_response({"transaction_id": transaction_id})