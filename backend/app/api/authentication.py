from flask_httpauth import HTTPBasicAuth
from flask import g, abort, request, jsonify
from ..models import User, Permission
from . import api_bp


auth = HTTPBasicAuth()
BYPASS_AUTH = ['api.v1.auth.login', 'api.v1.test']


@auth.verify_password
def verify_password(student_id_or_token, password):
    # 添加 g.token_used 的目的是为了让视图函数区分是使用 token 还是密码进行认证
    # 进一步防止用户绕过令牌过期机制
    g.is_anonymous = True
    g.token_used = False
    if request.endpoint in BYPASS_AUTH:
        return True
    if student_id_or_token:
        if password:
            user = User.query.filter_by(student_id=student_id_or_token).first()
            if user is None or not user.verify_password(password):
                return False
            if not user.can(Permission.LOGIN):
                return False
            g.current_user = user
            g.is_anonymous = False
            return True
        else:
            g.token_used = True
            user = User.verify_auth_token(student_id_or_token)
            if user is None or not user.can(Permission.LOGIN):
                return False
            g.is_anonymous = False
            g.current_user = user
            return True
    return False


@auth.error_handler
def unauthorized():
    response_json = {
        'success': False,
        'code': 400,
        'msg': 'Invalid credentials'
    }
    return jsonify(response_json), response_json['code']


@api_bp.before_request
@auth.login_required
def before_request():
    if not g.is_anonymous and not g.current_user.confirmed:
        # User is not confirmed
        response_json = {
            'success': False,
            'code': 403,
            'msg': 'User is not confirmed'
        }
        return jsonify(response_json), 403
