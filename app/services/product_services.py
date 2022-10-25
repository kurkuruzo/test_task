from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_model import Product
from app.models.account_model import Account
from app.models.transaction_model import Transaction
from app.services.account_services import check_balance, update_balance

class InsuficientBalance(Exception):
    pass

async def buy_product(session: AsyncSession, product_id: int, account_id: int) -> Transaction:
    product = await Product.get_by_id(session, product_id)
    transaction = Transaction(amount=-product.price, account_id=account_id)
    if await check_balance(session=session, transaction=transaction):
        await transaction.save(session)
    return transaction

