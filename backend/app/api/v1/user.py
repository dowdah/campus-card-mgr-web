from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission
from ... import db
from ...decorators import permission_required, operator_only
from datetime import datetime

user_bp = Blueprint('user', __name__)
EDITABLE_ATTRS = ['name', 'student_id', 'email', 'confirmed', 'comments']  # 操作人员可修改的用户属性


@user_bp.route('/query', methods=['GET', 'POST'])
@permission_required(Permission.VIEW_USER_INFO)
def get_users():
    # 查询所有符合条件的用户并分页返回
    users = None
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id', type=str)  # 如果 sort_by 不是 User 的属性则默认为 'id'
    sort_order = request.args.get('sort_order', 'asc', type=str)  # 如果 sort_order 不是 'desc' 则默认为 'asc'
    if request.method == 'GET':
        try:
            query = User.query.order_by(
                getattr(User, sort_by).desc() if sort_order == 'desc' else getattr(User, sort_by).asc())
        except AttributeError:
            sort_by = 'id'
            query = User.query.order_by(
                getattr(User, sort_by).desc() if sort_order == 'desc' else getattr(User, sort_by).asc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items
    elif request.method == 'POST':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']
        try:
            query = User.query.order_by(
                getattr(User, sort_by).desc() if sort_order == 'desc' else getattr(User, sort_by).asc())
        except AttributeError:
            sort_by = 'id'
            query = User.query.order_by(
                getattr(User, sort_by).desc() if sort_order == 'desc' else getattr(User, sort_by).asc())
        try:
            for k, v in g.data.items():
                if k == 'role_name':
                    query = query.filter(User.role.has(name=v))
                elif k in ['name', 'student_id', 'email', 'comments']:
                    query = query.filter(getattr(User, k).like(f"%{v}%"))
                elif k in ['start_date', 'end_date']:
                    try:
                        if k == 'start_date':
                            start_date = datetime.strptime(v, '%Y-%m-%d')
                            query = query.filter(User.created_at >= start_date)
                        elif k == 'end_date':
                            end_date = datetime.strptime(v, '%Y-%m-%d')
                            query = query.filter(User.created_at <= end_date)
                    except ValueError:
                        response_json = {
                            'success': False,
                            'code': 400,
                            'msg': 'Invalid date format. Use YYYY-MM-DD'
                        }
                        return jsonify(response_json), response_json['code']
                else:
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
            'users': [user.to_json(include_sensitive=True, include_related=False) for user in users],
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
            'msg': '未找到符合条件的用户。'
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
                'msg': '未提供修改数据'
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
                        'msg': '不可修改的参数: ' + ', '.join(unaccepted_attrs)
                    }
                else:
                    try:
                        for k, v in g.data.items():
                            setattr(user, k, v)
                        else:
                            db.session.add(user)
                            db.session.commit()
                            response_json = {
                                'success': True,
                                'code': 200,
                                'msg': '修改成功。'
                            }
                    except Exception as e:
                        db.session.rollback()
                        response_json = {
                            'success': False,
                            'code': 400,
                            'msg': '检查数据是否与已有用户重复。'
                        }
            else:
                response_json = {
                    'success': False,
                    'code': 404,
                    'msg': '用户不存在。'
                }
        else:
            response_json = {
                'success': False,
                'code': 403,
                'msg': '你没有权限修改用户信息。'
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
            'msg': '创建新用户失败，请检查学号、邮箱是否与已有用户重复。'
        }
    else:
        response_json = {
            'success': True,
            'code': 200,
            'msg': '新用户创建成功。'
        }
    return jsonify(response_json), response_json['code']
