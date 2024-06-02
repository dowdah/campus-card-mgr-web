from flask_httpauth import HTTPBasicAuth
from flask import g, abort, request, jsonify
from ..models import User


auth = HTTPBasicAuth()
BYPASS_AUTH = ['api_v1.login', 'api_v1.test']


from .v1 import api_v1


@auth.verify_password
def verify_password(alternative_id_or_token, password):
    # 添加 g.token_used 的目的是为了让视图函数区分是使用 token 还是密码进行认证
    # 进一步防止用户绕过令牌过期机制
    g.is_anonymous = True
    g.token_used = False
    if request.endpoint in BYPASS_AUTH:
        return True
    if alternative_id_or_token:
        if password:
            user = User.query.filter_by(alternative_id=alternative_id_or_token).first()
            if user is None:
                return False
            if not user.verify_password(password):
                return False
            g.current_user = user
            g.is_anonymous = False
            return True
        else:
            g.token_used = True
            user = User.verify_auth_token(alternative_id_or_token)
            if user is None:
                return False
            g.is_anonymous = False
            g.current_user = user
            return True
    return False


@auth.error_handler
def unauthorized():
    response_json = {
        'success': False,
        'code': 401,
        'description': 'Unauthorized access'
    }
    return jsonify(response_json), 401


@api_v1.before_request
@auth.login_required
def before_request():
    if not g.is_anonymous and not g.current_user.confirmed:
        # User is not confirmed
        response_json = {
            'success': False,
            'code': 403,
            'description': 'User is not confirmed'
        }
        return jsonify(response_json), 403
