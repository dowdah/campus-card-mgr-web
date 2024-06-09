from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission
from ... import db
from ...decorators import permission_required, operator_only


user_bp = Blueprint('user', __name__)
EDITABLE_ATTRS = ['name', 'student_id', 'email', 'confirmed', 'comments']  # 操作人员可修改的用户属性


@user_bp.route('/query', methods=['GET', 'POST'])
@permission_required(Permission.VIEW_USER_INFO)
def get_users():
    # 查询所有符合条件的用户并分页返回
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if request.method == 'GET':
        pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items
    elif request.method == 'POST':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']
        query = User.query
        try:
            for k, v in g.data.items():
                query = query.filter(getattr(User, k) == v)
        except AttributeError:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Invalid parameter'
            }
            return jsonify(response_json), response_json['code']
        else:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            users = pagination.items
    if users:
        response_json = {
            'success': True,
            'code': 200,
            'users': [user.to_json(include_sensitive=True) for user in users],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'next_num': pagination.next_num,
            'prev_num': pagination.prev_num
        }
    else:
        response_json = {
            'success': False,
            'code': 404,
            'msg': 'No user found'
        }
    return jsonify(response_json), response_json['code']


@user_bp.route('/operate/<int:id>', methods=['PUT', 'DELETE'])
@permission_required(Permission.VIEW_USER_INFO)
def operate_user(id):
    # 对特定ID的用户进行信息修改或删除
    user = User.query.filter_by(id=id).first()
    if request.method == 'PUT':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']
        if g.current_user.can(Permission.MODIFY_USER_INFO):
            if user:
                unaccepted_attrs = []
                for k in g.data.keys():
                    if k not in EDITABLE_ATTRS:
                        unaccepted_attrs.append(k)
                if unaccepted_attrs:
                    response_json = {
                        'success': False,
                        'code': 400,
                        'msg': 'Unacceptable attributes: ' + ', '.join(unaccepted_attrs)
                    }
                else:
                    for k, v in g.data.items():
                        setattr(user, k, v)
                    else:
                        db.session.add(user)
                        db.session.commit()
                        response_json = {
                            'success': True,
                            'code': 200,
                            'msg': 'User updated successfully'
                        }
            else:
                response_json = {
                    'success': False,
                    'code': 404,
                    'msg': 'User not found'
                }
        else:
            response_json = {
                'success': False,
                'code': 403,
                'msg': 'Permission denied'
            }
    elif request.method == 'DELETE':
        if g.current_user.can(Permission.DEL_USER):
            if user:
                if g.current_user == user:
                    response_json = {
                        'success': False,
                        'code': 403,
                        'msg': 'Cannot delete yourself'
                    }
                else:
                    db.session.delete(user)
                    db.session.commit()
                    response_json = {
                        'success': True,
                        'code': 200,
                        'msg': 'User deleted successfully'
                    }
            else:
                response_json = {
                    'success': False,
                    'code': 404,
                    'msg': 'User not found'
                }
        else:
            response_json = {
                'success': False,
                'code': 403,
                'msg': 'Permission denied'
            }
    return jsonify(response_json), response_json['code']


@user_bp.route('/new', methods=['POST'])
@permission_required(Permission.ADD_USER)
def new_user():
    # 创建新用户
    if g.data is None:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'No data provided'
        }
        return jsonify(response_json), response_json['code']
    try:
        user = User()
        for k, v in g.data.items():
            setattr(user, k, v)
        else:
            db.session.add(user)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'Invalid data provided'
        }
    else:
        response_json = {
            'success': True,
            'code': 200,
            'msg': 'User created successfully'
        }
    return jsonify(response_json), response_json['code']
