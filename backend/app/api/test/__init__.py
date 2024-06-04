from flask import Blueprint, abort

test_bp = Blueprint('test', __name__)


@test_bp.route('/')
def index():
    return abort(403)
