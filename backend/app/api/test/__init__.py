from flask import Blueprint, abort
from flask import current_app

test_bp = Blueprint('test', __name__)


@test_bp.route('/process/<name>')
def process(name):
    result = current_app.celery.send_task('app.reverse', args=[name])
    return f'Processing {name}'
