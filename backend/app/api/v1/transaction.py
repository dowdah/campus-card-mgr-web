from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission, Card, Transaction
from ... import db
from ...decorators import permission_required
from datetime import datetime

transaction_bp = Blueprint('transaction', __name__)


@transaction_bp.route('/query', methods=['GET', 'POST'])
@permission_required(Permission.VIEW_USER_INFO)
def get_transactions():
    # 查询所有符合条件的交易记录并分页返回
    transactions = None
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id', type=str)  # 如果 sort_by 不是 Transaction 的属性则默认为 'id'
    sort_order = request.args.get('sort_order', 'asc', type=str)  # 如果 sort_order 不是 'desc' 则默认为 'asc'
    if request.method == 'GET':
        try:
            query = Transaction.query.order_by(
                getattr(Transaction, sort_by).desc() if sort_order == 'desc' else getattr(Transaction, sort_by).asc())
        except AttributeError:
            sort_by = 'id'
            query = Transaction.query.order_by(
                getattr(Transaction, sort_by).desc() if sort_order == 'desc' else getattr(Transaction, sort_by).asc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        transactions = pagination.items
    elif request.method == 'POST':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']
        query = Transaction.query.order_by(Transaction.id.desc())
        start_date_str = g.data.get('start_date', None)
        end_date_str = g.data.get('end_date', None)
        try:
            query = Transaction.query.order_by(
                getattr(Transaction, sort_by).desc() if sort_order == 'desc' else getattr(Transaction, sort_by).asc())
        except AttributeError:
            sort_by = 'id'
            query = Transaction.query.order_by(
                getattr(Transaction, sort_by).desc() if sort_order == 'desc' else getattr(Transaction, sort_by).asc())
        try:
            for k, v in g.data.items():
                if k.startswith('user_'):
                    user_attr = k[k.find('_') + 1:]
                    query = query.filter(Transaction.user.has(getattr(User, user_attr).like('%' + str(v) + '%')))
                elif k.startswith('card_'):
                    card_attr = k[k.find('_') + 1:]
                    query = query.filter(Transaction.card.has(getattr(Card, card_attr).like('%' + str(v) + '%')))
                elif k.startswith('amount_'):
                    if k == 'amount_gt':
                        query = query.filter(Transaction.amount > v)
                    elif k == 'amount_lt':
                        query = query.filter(Transaction.amount < v)
                    else:
                        raise AttributeError(k)
                elif k in ['id', 'comments']:
                    query = query.filter(getattr(Transaction, k).like('%' + v + '%'))
                elif k in ['start_date', 'end_date']:
                    continue
                else:
                    query = query.filter(getattr(Transaction, k) == v)
        except AttributeError as e:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Invalid parameter: ' + str(e)
            }
            return jsonify(response_json), response_json['code']
        else:
            try:
                if start_date_str:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    query = query.filter(Transaction.created_at >= start_date)
                if end_date_str:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    query = query.filter(Transaction.created_at <= end_date)
            except ValueError:
                response_json = {
                    'success': False,
                    'code': 400,
                    'msg': 'Invalid date format. Use YYYY-MM-DD'
                }
                return jsonify(response_json), response_json['code']
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            transactions = pagination.items
    if transactions:
        response_json = {
            'success': True,
            'code': 200,
            'transactions': [transaction.to_json(include_sensitive=True) for transaction in transactions],
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
            'msg': '没有符合条件的交易。'
        }
    return jsonify(response_json), response_json['code']


@transaction_bp.route('/cancel/<int:id>', methods=['GET'])
@permission_required(Permission.CANCEL_TRANSACTION)
def cancel_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.is_canceled:
        response_json = {
            'success': False,
            'code': 400,
            'msg': '交易已撤销。'
        }
    else:
        if transaction.cancel():
            response_json = {
                'success': True,
                'code': 200,
                'msg': '交易撤销成功。'
            }
        else:
            response_json = {
                'success': False,
                'code': 400,
                'msg': '卡片余额不足，撤销失败。'
            }
    return jsonify(response_json), response_json['code']


@transaction_bp.route('/my/query', methods=['GET', 'POST'])
def get_my_transactions():
    # 查询所有符合条件的交易记录并分页返回
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    my_transactions = g.current_user.transactions

    if request.method == 'GET':
        pagination = my_transactions.order_by(Transaction.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        transactions = pagination.items
    elif request.method == 'POST':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']

        query = my_transactions.order_by(Transaction.id.desc())

        # 检查是否提供了时间范围
        start_date_str = g.data.get('start_date')
        end_date_str = g.data.get('end_date')

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                query = query.filter(Transaction.created_at >= start_date)
            except ValueError:
                response_json = {
                    'success': False,
                    'code': 400,
                    'msg': 'Invalid date format. Use YYYY-MM-DD'
                }
                return jsonify(response_json), response_json['code']

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                query = query.filter(Transaction.created_at <= end_date)
            except ValueError:
                response_json = {
                    'success': False,
                    'code': 400,
                    'msg': 'Invalid date format. Use YYYY-MM-DD'
                }
                return jsonify(response_json), response_json['code']

        try:
            for k, v in g.data.items():
                if k not in ['start_date', 'end_date']:
                    query = query.filter(getattr(Transaction, k) == v)
        except AttributeError:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Invalid parameter'
            }
            return jsonify(response_json), response_json['code']
        else:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            transactions = pagination.items

    if transactions:
        response_json = {
            'success': True,
            'code': 200,
            'transactions': [transaction.to_json() for transaction in transactions],
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
            'msg': 'No transaction found'
        }

    return jsonify(response_json), response_json['code']


@transaction_bp.route('/my/make', methods=['POST'])
def make_my_transaction():
    card_id = g.data.get('card_id')
    amount = g.data.get('amount')
    method = g.data.get('method')
    response_json = {}
    if not (card_id and amount and method):
        response_json = {
            'success': False,
            'code': 400,
            'msg': '缺失参数。'
        }
        return jsonify(response_json), response_json['code']
    card = g.current_user.cards.filter_by(id=card_id).first()
    if card:
        if card.is_active:
            if method == 'recharge':
                if card.recharge(amount):
                    response_json = {
                        'success': True,
                        'code': 200,
                        'msg': '充值成功。'
                    }
                else:
                    response_json = {
                        'success': False,
                        'code': 400,
                        'msg': '充值失败，检查参数是否正确。'
                    }
            elif method == 'consume':
                if card.consume(amount):
                    response_json = {
                        'success': True,
                        'code': 200,
                        'msg': '消费成功。'
                    }
                else:
                    response_json = {
                        'success': False,
                        'code': 400,
                        'msg': '消费失败，检查参数是否正确或余额是否充足。'
                    }
            else:
                response_json = {
                    'success': False,
                    'code': 400,
                    'msg': '参数错误: 无效的交易方式。'
                }
        else:
            response_json = {
                'success': False,
                'code': 400,
                'msg': '卡片状态异常，交易失败。'
            }
    else:
        response_json = {
            'success': False,
            'code': 400,
            'msg': '卡片未找到。'
        }
    return jsonify(response_json), response_json['code']
