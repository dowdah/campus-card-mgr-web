from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission
from ...decorators import permission_required


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
@permission_required(Permission.LOGIN)
def get_me():
    if not g.current_user.confirmed:
        response_json = {
            'success': False,
            'code': 403,
            'msg': '你的邮箱未确认，确认邮箱后才能登陆。'
        }
        return jsonify(response_json), response_json['code']
    response_json = {
        'success': True,
        'code': 200,
        'user': g.current_user.to_json()
    }
    return jsonify(response_json), response_json['code']


@auth_bp.route('/login', methods=['POST'])
def login():
    data = g.data
    student_id = data.get('student_id')
    password = data.get('password')
    if student_id and password:
        user = User.query.filter_by(student_id=student_id).first()
        if user:
            if user.can(Permission.LOGIN) and user.confirmed:
                if user.verify_password(password):
                    response_json = {
                        'success': True,
                        'code': 200,
                        'msg': '登录成功。',
                        'token': user.generate_auth_token(),
                        'expiration': current_app.config['API_TOKEN_EXPIRATION'],
                        'user': user.to_json()
                    }
                else:
                    response_json = {
                        'success': False,
                        'code': 401,
                        'msg': '用户名或密码错误。'
                    }
            else:
                response_json = {
                    'success': False,
                    'code': 403,
                    'msg': '你的邮箱未确认，确认邮箱后才能登陆。' if not user.confirmed else '你无权登录，联系管理员。'
                }
        else:
            response_json = {
                'success': False,
                'code': 401,
                'msg': '用户名或密码错误。'
            }
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': '参数错误。'
        }
    return jsonify(response_json), response_json['code']


@auth_bp.route('/refresh')
@permission_required(Permission.LOGIN)
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
