from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission, Card, Transaction
from ... import db
from ...decorators import permission_required
from datetime import datetime

card_bp = Blueprint('card', __name__)
EDITABLE_ATTRS = ['is_banned', 'is_lost', 'balance']  # 操作人员可修改的一卡通属性


@card_bp.route('/query', methods=['GET', 'POST'])
@permission_required(Permission.VIEW_USER_INFO)
def get_cards():
    # 查询所有符合条件的一卡通并分页返回
    cards = None
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id', type=str)  # 如果 sort_by 不是 Card 的属性则默认为 'id'
    sort_order = request.args.get('sort_order', 'asc', type=str)  # 如果 sort_order 不是 'desc' 则默认为 'asc'
    if request.method == 'GET':
        try:
            query = Card.query.order_by(
                getattr(Card, sort_by).desc() if sort_order == 'desc' else getattr(Card, sort_by).asc())
        except AttributeError:
            sort_by = 'id'
            query = Card.query.order_by(
                getattr(Card, sort_by).desc() if sort_order == 'desc' else getattr(Card, sort_by).asc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        cards = pagination.items
    elif request.method == 'POST':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']
        try:
            query = Card.query.order_by(
                getattr(Card, sort_by).desc() if sort_order == 'desc' else getattr(Card, sort_by).asc())
        except AttributeError:
            sort_by = 'id'
            query = Card.query.order_by(
                getattr(Card, sort_by).desc() if sort_order == 'desc' else getattr(Card, sort_by).asc())
        try:
            for k, v in g.data.items():
                if k.startswith('user_'):
                    user_attr = k[k.find('_') + 1:]
                    query = query.filter(Card.user.has(getattr(User, user_attr).like(f"%{v}%")))
                elif k.startswith('balance_'):
                    if k == 'balance_gt':
                        query = query.filter(Card.balance > v)
                    elif k == 'balance_lt':
                        query = query.filter(Card.balance < v)
                    else:
                        raise AttributeError(k)
                elif k in ['start_created_date', 'end_created_date', 'start_expires_date', 'end_expires_date']:
                    try:
                        if k == 'start_created_date':
                            start_created_date = datetime.strptime(v, '%Y-%m-%d')
                            query = query.filter(Card.created_at >= start_created_date)
                        elif k == 'end_created_date':
                            end_created_date = datetime.strptime(v, '%Y-%m-%d')
                            query = query.filter(Card.created_at <= end_created_date)
                        elif k == 'start_expires_date':
                            start_expires_date = datetime.strptime(v, '%Y-%m-%d')
                            query = query.filter(Card.expires_at >= start_expires_date)
                        elif k == 'end_expires_date':
                            end_expires_date = datetime.strptime(v, '%Y-%m-%d')
                            query = query.filter(Card.expires_at <= end_expires_date)
                    except ValueError:
                        response_json = {
                            'success': False,
                            'code': 400,
                            'msg': 'Invalid date format. Use YYYY-MM-DD'
                        }
                        return jsonify(response_json), response_json['code']
                else:
                    query = query.filter(getattr(Card, k) == v)
        except AttributeError as e:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Invalid parameter: ' + str(e)
            }
            return jsonify(response_json), response_json['code']
        else:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            cards = pagination.items
    if cards:
        response_json = {
            'success': True,
            'code': 200,
            'cards': [card.to_json() for card in cards],
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
            'msg': '未找到符合条件的一卡通。'
        }
    return jsonify(response_json), response_json['code']


@card_bp.route('/set/<int:id>', methods=['PUT'])
def set_card(id):
    # 修改一卡通 is_banned, is_lost, balance 属性
    if not (g.current_user.can(Permission.CHANGE_CARD_STATUS) or g.current_user.can(Permission.CHANGE_CARD_BALANCE)):
        abort(403)
    data = g.data
    if data:
        unaccepted_attrs = []
        for k in data.keys():
            if k not in EDITABLE_ATTRS:
                unaccepted_attrs.append(k)
        if unaccepted_attrs:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Unaccepted attributes: ' + ', '.join(unaccepted_attrs)
            }
            return jsonify(response_json), response_json['code']
        if 'balance' in data.keys() and not g.current_user.can(Permission.CHANGE_CARD_BALANCE):
            response_json = {
                'success': False,
                'code': 403,
                'msg': 'Permission denied'
            }
            return jsonify(response_json), response_json['code']
        if (('is_banned' in data.keys() or 'is_lost' in data.keys())
                and not g.current_user.can(Permission.CHANGE_CARD_STATUS)):
            response_json = {
                'success': False,
                'code': 403,
                'msg': 'Permission denied'
            }
            return jsonify(response_json), response_json['code']
        card = Card.query.filter_by(id=id).first()
        if card is None:
            response_json = {
                'success': False,
                'code': 404,
                'msg': 'Card not found'
            }
            return jsonify(response_json), response_json['code']
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'No data provided'
        }
        return jsonify(response_json), response_json['code']
    for k, v in data.items():
        try:
            setattr(card, k, v)
            db.session.add(card)
            db.session.commit()
        except Exception as e:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Invalid parameter: ' + str(e)
            }
        else:
            response_json = {
                'success': True,
                'code': 200,
                'msg': '卡片信息更新成功。'
            }
    return jsonify(response_json), response_json['code']


@card_bp.route('/renew/<int:id>', methods=['PUT'])
@permission_required(Permission.CHANGE_CARD_STATUS)
def renew_card(id):
    # 延长一卡通有效期
    if g.data is None:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'No data provided'
        }
        return jsonify(response_json), response_json['code']
    else:
        renew_days = 0
        try:
            year = g.data.get('year')
            month = g.data.get('month')
            week = g.data.get('week')
            day = g.data.get('day')
            renew_days += 365 * int(year) if year else 0
            renew_days += 30 * int(month) if month else 0
            renew_days += 7 * int(week) if week else 0
            renew_days += int(day) if day else 0
        except Exception as e:
            response_json = {
                'success': False,
                'code': 400,
                'msg': '不合法的参数: ' + str(e)
            }
            return jsonify(response_json), response_json['code']
        if renew_days == 0:
            response_json = {
                'success': False,
                'code': 400,
                'msg': '参数不合法。'
            }
            return jsonify(response_json), response_json['code']
        else:
            card = Card.query.filter_by(id=id).first()
            if card:
                card.renew(renew_days)
                response_json = {
                    'success': True,
                    'code': 200,
                    'msg': '卡片延期成功。'
                }
            else:
                response_json = {
                    'success': False,
                    'code': 404,
                    'msg': '未找到该一卡通。'
                }
            return jsonify(response_json), response_json['code']


@card_bp.route('/create/<int:id>', methods=['GET', 'POST'])
@permission_required(Permission.ADD_CARD)
def create_card(id):
    # 为用户创建一卡通
    user = User.query.filter_by(id=id).first()
    if user is None:
        response_json = {
            'success': False,
            'code': 404,
            'msg': 'User not found'
        }
        return jsonify(response_json), response_json['code']
    if request.method == 'GET':
        card = Card(user=user)
        db.session.add(card)
        db.session.commit()
        response_json = {
            'success': True,
            'code': 200,
            'msg': '一卡通创建成功。'
        }
    elif request.method == 'POST':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']
        card = Card(user=user)
        for k, v in g.data.items():
            if k in EDITABLE_ATTRS:
                setattr(card, k, v)
            elif k == 'expires_at':
                expires_at = datetime.strptime(v, '%Y-%m-%d')
                card.expires_at = expires_at
            else:
                response_json = {
                    'success': False,
                    'code': 400,
                    'msg': 'Unaccepted attributes: ' + k
                }
                break
        else:
            db.session.add(card)
            db.session.commit()
            response_json = {
                'success': True,
                'code': 200,
                'msg': '一卡通创建成功。'
            }
    return jsonify(response_json), response_json['code']


@card_bp.route('/rm/<int:id>', methods=['DELETE'])
@permission_required(Permission.DEL_CARD)
def delete_card(id):
    card = Card.query.filter_by(id=id).first()
    if card:
        db.session.delete(card)
        db.session.commit()
        response_json = {
            'success': True,
            'code': 200,
            'msg': '卡片删除成功。'
        }
    else:
        response_json = {
            'success': False,
            'code': 404,
            'msg': '未找到该一卡通。'
        }
    return jsonify(response_json), response_json['code']


@card_bp.route('/my')
def get_my_cards():
    response_json = {
        'success': True,
        'code': 200,
        'cards': [card.to_json() for card in g.current_user.cards]
    }
    return jsonify(response_json), response_json['code']


@card_bp.route('/my/<int:id>')
def get_my_card(id):
    card = g.current_user.cards.filter_by(id=id).first()
    if card:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        pagination = card.transactions.order_by(Transaction.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        transactions = pagination.items
        card_json = card.to_json(include_related=False)
        card_json['transactions'] = [transaction.to_json(include_related=False) for transaction in transactions]
        response_json = {
            'success': True,
            'code': 200,
            'card': card_json,
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
            'msg': '未找到该一卡通。'
        }
    return jsonify(response_json), response_json['code']


@card_bp.route('/my/lost/<int:id>')
def report_card_lost(id):
    card = g.current_user.cards.filter_by(id=id).first()
    if card:
        if card.is_lost:
            response_json = {
                'success': False,
                'code': 400,
                'msg': '卡片已被挂失。'
            }
        else:
            card.is_lost = True
            db.session.add(card)
            db.session.commit()
            response_json = {
                'success': True,
                'code': 200,
                'msg': '卡片挂失成功。'
            }
    else:
        response_json = {
            'success': False,
            'code': 404,
            'msg': '未找到该一卡通。'
        }
    return jsonify(response_json), response_json['code']
