from flask import Blueprint

v1_bp = Blueprint('v1', __name__)

from . import errors, views
from .auth import auth_bp
from .user import user_bp
from .card import card_bp

v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
v1_bp.register_blueprint(user_bp, url_prefix='/user')
v1_bp.register_blueprint(card_bp, url_prefix='/card')
