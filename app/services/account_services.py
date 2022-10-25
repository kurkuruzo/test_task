import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account_model import Account

logger = logging.getLogger(__name__)
# from app.models.transaction_model import Transaction


class AccountException(Exception):
    pass

async def check_balance(session: AsyncSession, transaction) -> None:
    try:
        account = await Account.get_by_id(session, transaction.account_id)
    except Exception:
        raise AccountException
    return account.balance + transaction.amount > 0

    
async def update_balance(session: AsyncSession, account_id: int, amount: float):
    try:
        account = await Account.get_by_id(session, account_id)
    except Exception:
        raise AccountException("Account not found")
    account.balance += amount
    # session.add(account)
    await session.commit()
    logger.info(f"{account.balance}")
    return account