from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission, Card
from ... import db


card_bp = Blueprint('card', __name__)


@card_bp.route('/query', methods=['GET', 'POST'])
def get_cards():
    # 查询所有符合条件的一卡通并分页返回
    if not g.current_user.can(Permission.VIEW_USER_INFO):
        response_json = {
            'success': False,
            'code': 403,
            'msg': 'Permission denied'
        }
        return jsonify(response_json), response_json['code']
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if request.method == 'GET':
        pagination = Card.query.paginate(page=page, per_page=per_page, error_out=False)
        cards = pagination.items
    elif request.method == 'POST':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']
        query = Card.query
        try:
            for k, v in g.data.items():
                query = query.filter(getattr(Card, k) == v)
        except AttributeError:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Invalid parameter'
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
            'msg': 'No card found'
        }
    return jsonify(response_json), response_json['code']
