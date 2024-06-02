from . import api_v1
from flask import jsonify, request, g, abort, current_app
from ...models import User, Permission


@api_v1.before_request
def before_request():
    # 将 application/json 与 multipart/form-data 的数据统一处理
    # g.temp = request.content_type
    if request.method == 'POST':
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


@api_v1.route('/test', methods=['GET', 'POST'])
def test():
    return {'status': 'success', 'msg': g.temp}


@api_v1.route('/users')
def get_users():
    if g.current_user.can(Permission.VIEW_USER_INFO):
        users = User.query.all()
        response_json = {
            'success': True,
            'code': 200,
            'users': [user.to_json() for user in users]
        }
    else:
        response_json = {
            'success': False,
            'code': 403,
            'msg': 'Permission denied'
        }
    return jsonify(response_json), response_json['code']


@api_v1.route('/login', methods=['POST'])
def login():
    """
    code:
    200: 登录成功
    400: 参数错误
    401: 用户名或密码错误
    """
    data = g.data
    username = data.get('username')
    password = data.get('password')
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            response_json = {
                'success': True,
                'code': 200,
                'msg': 'Login successfully',
                'token': user.generate_auth_token(),
                'expiration': current_app.config['API_TOKEN_EXPIRATION']
            }
        else:
            response_json = {
                'success': False,
                'code': 401,
                'msg': 'Invalid credentials'
            }
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'Invalid parameters'
        }
    return jsonify(response_json), response_json['code']


@api_v1.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        response_json = {
            'success': False,
            'code': 403,
            'msg': 'Unauthorized access'
        }
    response_json = {
        'success': True,
        'code': 200,
        'msg': 'Token generated successfully',
        'token': g.current_user.generate_auth_token(),
        'expiration': current_app.config['API_TOKEN_EXPIRATION']
    }
    return jsonify(response_json), response_json['code']


@api_v1.route('/me')
def get_me():
    response_json = {
        'success': True,
        'code': 200,
        'user': g.current_user.to_json()
    }
    return jsonify(response_json), response_json['code']
