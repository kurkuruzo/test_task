from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response
from app.models.transaction_model import Transaction
from app.services.user_services import protected
from app.services.transaction_services import TransactionError, process_payment

transaction_bp = Blueprint("transaction_blueprint")

@transaction_bp.post('/transactions')
@protected
async def create_transaction(request: Request) -> HTTPResponse:
    session = request.ctx.session
    body = request.json
    transaction = Transaction(account_id=body['account_id'], amount=body['amount'])
    await transaction.save(session)
    return json_response(transaction.to_dict(), status=201)

@transaction_bp.get('/transactions')
@protected
async def get_transactions(request: Request) -> HTTPResponse:
    session = request.ctx.session
    transactions = await Transaction.get_all(session)
    return json_response([transaction.to_dict() for transaction in transactions])
    
@transaction_bp.get('/transactions/<pk:int>')
@protected
async def get_transaction(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    transaction = await Transaction.get_by_id(session, pk)
    if not transaction:
        return HTTPResponse(status=404)
    return json_response(transaction.to_dict())

@transaction_bp.delete('/transactions/<pk:int>')
@protected
async def delete_transaction(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    transaction = await Transaction.get_by_id(session, pk)
    if not transaction:
        return HTTPResponse(status=404)
    transaction_id = transaction.id
    await session.delete(transaction)
    await session.commit()
    return json_response({"transaction_id": transaction_id})

@transaction_bp.post('/payment/webhook')
async def payment(request: Request) -> HTTPResponse:
    body = request.json
    try:
        transaction = await process_payment(request.ctx.session, body)
    except TransactionError as e:
        return json_response({"result": "failed", "message": e.args[0]}, status=400)
    return json_response(transaction.to_dict())
