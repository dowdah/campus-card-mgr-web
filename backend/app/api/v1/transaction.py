from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission, Card, Transaction
from ... import db
from ...decorators import permission_required


transaction_bp = Blueprint('transaction', __name__)


@transaction_bp.route('/query', methods=['GET', 'POST'])
@permission_required(Permission.VIEW_USER_INFO)
def get_transactions():
    # 查询所有符合条件的交易记录并分页返回
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if request.method == 'GET':
        pagination = Transaction.query.order_by(Transaction.id.desc()).paginate(
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
        query = Transaction.query.order_by(Transaction.id.desc())
        try:
            for k, v in g.data.items():
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


@transaction_bp.route('/cancel/<int:id>', methods=['GET'])
@permission_required(Permission.CANCEL_TRANSACTION)
def cancel_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.is_canceled:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'Transaction already canceled'
        }
    else:
        if transaction.cancel():
            response_json = {
                'success': True,
                'code': 200,
                'msg': 'Transaction canceled successfully'
            }
        else:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Transaction cancel failed: insufficient balance'
            }
    return jsonify(response_json), response_json['code']
