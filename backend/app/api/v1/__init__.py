from flask import Blueprint

v1_bp = Blueprint('v1', __name__)

from . import errors, views
from .auth import auth_bp
from .user import user_bp
from .card import card_bp
from .transaction import transaction_bp
from .financial_report import fr_bp

v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
v1_bp.register_blueprint(user_bp, url_prefix='/user')
v1_bp.register_blueprint(card_bp, url_prefix='/card')
v1_bp.register_blueprint(transaction_bp, url_prefix='/transaction')
v1_bp.register_blueprint(fr_bp, url_prefix='/fr')
