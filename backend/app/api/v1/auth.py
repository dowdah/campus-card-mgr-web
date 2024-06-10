from flask import jsonify, request, g, abort, current_app, Blueprint, request
from ...models import User, Permission
from ...decorators import permission_required
from ... import db

auth_bp = Blueprint('auth', __name__)
ALLOW_TOKEN_REFRESH = True  # 是否允许使用 token 刷新 token，若不允许，客户端将总是在登录有限时长后被要求重新登录


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
    response_json = {
        'success': True,
        'code': 200,
        'user': g.current_user.to_json()
    }
    if ALLOW_TOKEN_REFRESH:
        response_json['token'] = g.current_user.generate_auth_token()
        response_json['expiration'] = current_app.config['API_TOKEN_EXPIRATION']
    return jsonify(response_json), response_json['code']


@auth_bp.route('/login', methods=['POST'])
def login():
    data = g.data
    student_id = data.get('student_id')
    email = data.get('email')
    password = data.get('password')
    user, user_1, user_2 = None, None, None
    if student_id:
        user_1 = User.query.filter_by(student_id=student_id).first()
    if email:
        user_2 = User.query.filter_by(email=email).first()
    if user_1 and user_2:
        return abort(400)
    elif user_1:
        user = user_1
    elif user_2:
        user = user_2
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': '凭据错误，核查你输入的信息是否正确。'
        }
        return jsonify(response_json), response_json['code']
    if user.can(Permission.LOGIN):
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
                'msg': '凭据错误。'
            }
    else:
        response_json = {
            'success': False,
            'code': 403,
            'msg': '你被禁止登录，联系管理员。'
        }
    return jsonify(response_json), response_json['code']


@auth_bp.route('/send-confirmation')
def send_confirmation():
    if g.current_user.confirmed:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'User already confirmed'
        }
    else:
        task = current_app.celery.send_task('app.send_email', args=[[g.current_user.email],
                                                                    "请确认您的账户", "auth/email_confirm.html"],
                                            kwargs={'token': g.current_user.generate_token(), 'user': g.current_user.to_json()})
        response_json = {
            'success': True,
            'code': 200,
            'msg': 'Confirmation email sent',
            'task_id': task.id
        }
    return jsonify(response_json), response_json['code']


@auth_bp.route('/confirm/<token>')
def confirm(token):
    if g.current_user.confirmed:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'User already confirmed'
        }
    elif g.current_user.validate_token(token):
        g.current_user.confirmed = True
        db.session.add(g.current_user)
        db.session.commit()
        response_json = {
            'success': True,
            'code': 200,
            'msg': 'User confirmed'
        }
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': '验证码错误。'
        }
    return jsonify(response_json), response_json['code']


@auth_bp.route('/reset-password')
def send_reset_password_email():
    student_id = request.args.get('student_id')
    email = request.args.get('email')
    user, user_1, user_2 = None, None, None
    if student_id:
        user_1 = User.query.filter_by(student_id=student_id).first()
    if email:
        user_2 = User.query.filter_by(email=email).first()
    if user_1 and user_2:
        if user_1 != user_2:
            response_json = {
                'success': False,
                'code': 400,
                'msg': '参数错误'
            }
            return jsonify(response_json), response_json['code']
        else:
            user = user_1
    elif user_1:
        user = user_1
    elif user_2:
        user = user_2
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': '不会有人把账号密码都忘了吧？'
        }
        return jsonify(response_json), response_json['code']
    task = current_app.celery.send_task('app.send_email', args=[[user.email],
                                                                "重置密码", "auth/email_password_reset.html"],
                                        kwargs={'token': user.generate_token(), 'user': user.to_json()})
    response_json = {
        'success': True,
        'code': 200,
        'msg': 'Reset password email sent',
        'task_id': task.id
    }
    return jsonify(response_json), response_json['code']


@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    student_id = g.data.get('student_id')
    email = g.data.get('email')
    password = g.data.get('password')
    user, user_1, user_2 = None, None, None
    if student_id:
        user_1 = User.query.filter_by(student_id=student_id).first()
    if email:
        user_2 = User.query.filter_by(email=email).first()
    if user_1 and user_2:
        if user_1 != user_2:
            response_json = {
                'success': False,
                'code': 400,
                'msg': '参数错误'
            }
            return jsonify(response_json), response_json['code']
        else:
            user = user_1
    elif user_1:
        user = user_1
    elif user_2:
        user = user_2
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': '参数错误'
        }
        return jsonify(response_json), response_json['code']
    if user.validate_token(token):
        user.password = password
        user.alternative_id = User.generate_alternative_id()
        db.session.add(user)
        db.session.commit()
        current_app.celery.send_task('app.send_email', args=[[user.email],
                                                             "密码重置成功", "auth/email_password_reset.html"],
                                     kwargs={'user': user.to_json()})
        response_json = {
            'success': True,
            'code': 200,
            'msg': '密码重置成功',
            'user': user.to_json(),
            'token': user.generate_auth_token(),
            'expiration': current_app.config['API_TOKEN_EXPIRATION']
        }
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'Token 不合法'
        }
    return jsonify(response_json), response_json['code']
