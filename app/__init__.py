import logging
from sanic import Sanic
from app import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

app = Sanic('app')
app.config.SECRET = config.SECRET

from app.blueprints.user_blueprints import user_bp
from app.blueprints.product_blueprints import product_bp
from app.blueprints.account_blueprints import account_bp
from app.blueprints.transaction_blueprints import transaction_bp
app.blueprint(user_bp)
app.blueprint(product_bp)
app.blueprint(account_bp)
app.blueprint(transaction_bp)