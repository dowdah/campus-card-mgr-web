from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission, Card, Transaction, FinancialReport
from ... import db
from ...decorators import permission_required


fr_bp = Blueprint('financial_report', __name__)


@fr_bp.route('/query', methods=['GET', 'POST'])
@permission_required(Permission.EXPORT_REPORTS)
def get_reports():
    # 查询所有符合条件的财务报表并分页返回
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if request.method == 'GET':
        pagination = FinancialReport.query.order_by(FinancialReport.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        reports = pagination.items
    elif request.method == 'POST':
        if g.data is None:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
            return jsonify(response_json), response_json['code']
        query = FinancialReport.query.order_by(FinancialReport.created_at.desc())
        try:
            for k, v in g.data.items():
                query = query.filter(getattr(FinancialReport, k) == v)
        except AttributeError:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'Invalid parameter'
            }
            return jsonify(response_json), response_json['code']
        else:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            reports = pagination.items
    if reports:
        response_json = {
            'success': True,
            'code': 200,
            'reports': [report.to_json() for report in reports],
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
            'msg': 'No report found'
        }
    return jsonify(response_json), response_json['code']
