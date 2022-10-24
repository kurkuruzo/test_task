from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_model import Product
from app.models.account_model import Account
from app.models.transaction_model import Transaction

class InsuficientBalance(Exception):
    pass

async def buy_product(session: AsyncSession, product_id: int, account_id: int) -> Transaction:
    product = await Product.get_by_id(session, product_id)
    transaction = Transaction(amount=-product.price, account_id=account_id)
    await _calculate_balance(session=session, transaction=transaction)
    await session.commit()
    return transaction

async def _calculate_balance(session: AsyncSession, transaction: Transaction) -> None:
    account = await Account.get_by_id(session, transaction.account_id)
    if account.balance + transaction.amount < 0:
        raise InsuficientBalance("Not enough money to buy")
    account.balance += transaction.amount
    session.add(transaction)
    session.add(account)