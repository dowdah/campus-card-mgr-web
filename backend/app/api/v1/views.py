from . import v1_bp
from flask import jsonify, request, g, abort, current_app, abort
from ...models import User, Permission


@v1_bp.before_request
def before_request():
    # 将 application/json 与 multipart/form-data 的数据统一处理
    # g.temp = request.content_type
    methods_with_body = ['POST', 'PUT', 'PATCH']
    if request.method in methods_with_body:
        if request.content_type:
            if 'application/json' in request.content_type:
                g.data = request.get_json()
                g.files = None
            elif 'multipart/form-data' in request.content_type:
                g.data = request.form.to_dict()
                g.files = request.files
            else:
                g.data = None
                g.files = None
        else:
            g.data = None
            g.files = None
    else:
        g.data = None
        g.files = None
    if g.data:
        g.data = {k: v for k, v in g.data.items() if v is not None}


@v1_bp.route('/permissions')
def get_permission_info():
    response_json = {
        'success': True,
        'code': 200,
        'permissions': Permission.to_json()
    }
    return jsonify(response_json), response_json['code']
