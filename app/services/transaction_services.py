import logging
from Crypto.Hash import SHA1
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypedDict
import app.config as config
from app.models.transaction_model import Transaction

logger = logging.getLogger(__name__)

class TransactionError(Exception):
    """Transaction failed"""
 
class Payment(TypedDict):
    signature: str
    transaction_id: int
    user_id: int
    bill_id: int
    amount: float
    
async def process_payment(session: AsyncSession, body: Payment) -> Transaction:
    transaction = await _parse_payment(body=body)
    await transaction.save(session)
    return transaction
 
 
async def _check_signature(body: Payment) -> bool:
    private_key = config.PRIVATE_KEY
    logger.info(f"{body=}")
    calculated_signature = SHA1.new()
    calculated_signature.update(f'{private_key}:{body["transaction_id"]}:{body["user_id"]}:{body["bill_id"]}:{body["amount"]}'.encode())
    logger.info(f"{calculated_signature.hexdigest()=}")
    return body["signature"] == calculated_signature.hexdigest()


async def _parse_payment(body: Payment) -> Transaction:
    if await _check_signature(body):
        payment = Transaction(
             account_id = body["bill_id"],
             amount = body["amount"],
        )
        logger.info(f'{payment=}')
        return payment
    raise TransactionError("Incorrect signature")
        