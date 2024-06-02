from . import api_v1
from flask import jsonify, request, g, abort, current_app
from ...models import User


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
    users = User.query.all()
    return jsonify([{'username': user.username, 'email': user.email} for user in users])


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
                'description': 'Login successfully',
                'token': user.generate_auth_token(),
                'expiration': current_app.config['API_TOKEN_EXPIRATION']
            }
        else:
            response_json = {
                'success': False,
                'code': 401,
                'description': 'Invalid credentials'
            }
    else:
        response_json = {
            'success': False,
            'code': 400,
            'description': 'Invalid parameters'
        }
    return jsonify(response_json), response_json['code']


@api_v1.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        response_json = {
            'success': False,
            'code': 403,
            'description': 'Unauthorized access'
        }
    response_json = {
        'success': True,
        'code': 200,
        'description': 'Token generated successfully',
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
