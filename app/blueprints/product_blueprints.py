from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.response import json as json_response
from app.models.product_model import Product
import app.services.product_services as pr_services
from app.services.user_services import admin, protected

product_bp = Blueprint("product_blueprint")

@product_bp.post('/products')
@admin
async def create_product(request: Request) -> HTTPResponse:
    session = request.ctx.session
    body = request.json
    async with session.begin():
        product = Product(title=body['title'], description=body['description'], price=body["price"])
        session.add_all([product])
    return json_response(product.to_dict(), status=201)

@product_bp.get('/products')
@protected
async def get_products(request: Request) -> HTTPResponse:
    session = request.ctx.session
    products = await Product.get_all(session)
    return json_response([product.to_dict() for product in products])
    
@product_bp.get('/products/<pk:int>')
@admin
async def get_product(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    product = await Product.get_by_id(session, pk)
    if not product:
        return HTTPResponse(status=404)
    return json_response(product.to_dict())

@product_bp.put('/products/<pk:int>')
@admin
async def update_product(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    new_title = request.json.get('title')
    new_description = request.json.get('description')
    new_price = request.json.get('price')
    product = await Product.get_by_id(session, pk)
    if not product:
        return HTTPResponse(status=404)
    if new_title:
        product.title = new_title
    elif new_description:
        product.description = new_description
    elif new_price:
        product.price = new_price
    await session.commit()
    return json_response(product.to_dict())

@admin
@product_bp.delete('/products/<pk:int>')
async def delete_product(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    product = await Product.get_by_id(session, pk)
    if not product:
        return HTTPResponse(status=404)
    product_id = product.id
    await session.delete(product)
    await session.commit()
    return json_response({"product_id": product_id})

@protected
@product_bp.post('/products/<pk:int>/order')
async def order_product(request: Request, pk: int) -> HTTPResponse:
    session = request.ctx.session
    account_id = request.json["account_id"]
    if not await Product.get_by_id(session, pk):
        return HTTPResponse(status=404)
    try:
        transaction = await pr_services.buy_product(session=session, product_id=pk, account_id=account_id)
    except pr_services.InsuficientBalance as e:
        return json_response({"result": "failed", "message": e.args}, status=409)
    return json_response(transaction.to_dict())