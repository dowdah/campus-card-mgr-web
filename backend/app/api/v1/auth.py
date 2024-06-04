from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission


auth_bp = Blueprint('auth', __name__)
ALLOW_TOKEN_REFRESH = True  # 是否允许使用 token 刷新 token，若不允许，客户端将在 token 过期后被要求重新登录


@auth_bp.before_request
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


@auth_bp.route('/me')
def get_me():
    response_json = {
        'success': True,
        'code': 200,
        'user': g.current_user.to_json()
    }
    return jsonify(response_json), response_json['code']


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    code:
    200: 登录成功
    400: 参数错误
    401: 用户名或密码错误
    """
    data = g.data
    student_id = data.get('student_id')
    password = data.get('password')
    if student_id and password:
        user = User.query.filter_by(student_id=student_id).first()
        if user and user.verify_password(password):
            response_json = {
                'success': True,
                'code': 200,
                'msg': 'Login successfully',
                'token': user.generate_auth_token(),
                'expiration': current_app.config['API_TOKEN_EXPIRATION'],
                'user': user.to_json()
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


@auth_bp.route('/refresh')
def get_token():
    if g.token_used and not ALLOW_TOKEN_REFRESH:
        response_json = {
            'success': False,
            'code': 401,
            'msg': 'Users are prohibited from using token to get token'
        }
    else:
        response_json = {
            'success': True,
            'code': 200,
            'msg': 'Token generated successfully',
            'token': g.current_user.generate_auth_token(),
            'expiration': current_app.config['API_TOKEN_EXPIRATION']
        }
    return jsonify(response_json), response_json['code']
