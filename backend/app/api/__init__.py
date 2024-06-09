from flask import Blueprint, current_app, jsonify

api_bp = Blueprint('api', __name__)

from .v1 import v1_bp
from .test import test_bp
from . import authentication, errors

api_bp.register_blueprint(v1_bp, url_prefix='/v1')
api_bp.register_blueprint(test_bp, url_prefix='/test')


@api_bp.route('/task/<task_id>')
def get_task(task_id):
    task = current_app.celery.AsyncResult(task_id)
    response_json = {'success': True, 'code': 200, 'task_status': task.status, 'task_result': task.result}
    return jsonify(response_json), response_json['code']
