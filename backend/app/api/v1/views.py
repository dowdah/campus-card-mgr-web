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
        g.data = {k: v for k, v in g.data.items() if v}


@v1_bp.route('/test', methods=['GET', 'POST'])
def test():
    # 测试用路由，生产环境中应删除
    # return {'status': 'success', 'msg': g.temp}
    return abort(403)
