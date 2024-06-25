from flask import jsonify, request, g, abort, current_app, Blueprint, send_file, url_for
from ...models import User, Permission, Card, Transaction, FinancialReport
from ... import db
from ...decorators import permission_required
from datetime import datetime
import io

fr_bp = Blueprint('financial_report', __name__)


@fr_bp.route('/query', methods=['GET', 'POST'])
@permission_required(Permission.EXPORT_REPORTS)
def get_reports():
    # 查询所有符合条件的财务报表并分页返回
    reports = None
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id', type=str)  # 如果 sort_by 不是 FR 的属性则默认为 'id'
    sort_order = request.args.get('sort_order', 'asc', type=str)  # 如果 sort_order 不是 'desc' 则默认为 'asc'
    if request.method == 'GET':
        try:
            query = FinancialReport.query.order_by(
                getattr(FinancialReport, sort_by).desc() if sort_order == 'desc' else getattr(FinancialReport,
                                                                                              sort_by).asc())
        except AttributeError:
            sort_by = 'id'
            query = FinancialReport.query.order_by(
                getattr(FinancialReport, sort_by).desc() if sort_order == 'desc' else getattr(FinancialReport,
                                                                                              sort_by).asc())
        pagination = query.order_by(FinancialReport.id.desc()).paginate(
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
        try:
            query = FinancialReport.query.order_by(
                getattr(FinancialReport, sort_by).desc() if sort_order == 'desc' else getattr(FinancialReport,
                                                                                              sort_by).asc())
        except AttributeError:
            sort_by = 'id'
            query = FinancialReport.query.order_by(
                getattr(FinancialReport, sort_by).desc() if sort_order == 'desc' else getattr(FinancialReport,
                                                                                              sort_by).asc())
        try:
            for k, v in g.data.items():
                if k.startswith('user_'):
                    user_attr = k[k.find('_') + 1:]
                    query = query.filter(FinancialReport.user.has(getattr(User, user_attr).like('%' + str(v) + '%')))
                elif k.startswith('total_income_'):
                    if k == 'total_income_gt':
                        query = query.filter(FinancialReport.total_income > v)
                    elif k == 'total_income_lt':
                        query = query.filter(FinancialReport.total_income < v)
                    else:
                        raise AttributeError(k)
                elif k.startswith('total_expenses_'):
                    if k == 'total_expenses_gt':
                        query = query.filter(FinancialReport.total_expenses > v)
                    elif k == 'total_expenses_lt':
                        query = query.filter(FinancialReport.total_expenses < v)
                    else:
                        raise AttributeError(k)
                elif k.startswith('net_growth_'):
                    if k == 'net_growth_gt':
                        query = query.filter(FinancialReport.net_growth > v)
                    elif k == 'net_growth_lt':
                        query = query.filter(FinancialReport.net_growth < v)
                    else:
                        raise AttributeError(k)
                elif k in ['start_date', 'end_date']:
                    try:
                        if k == 'start_date':
                            start_date = datetime.strptime(v, '%Y-%m-%d')
                            query = query.filter(FinancialReport.created_at >= start_date)
                        elif k == 'end_date':
                            end_date = datetime.strptime(v, '%Y-%m-%d')
                            query = query.filter(FinancialReport.created_at <= end_date)
                    except ValueError:
                        response_json = {
                            'success': False,
                            'code': 400,
                            'msg': 'Invalid date format. Use YYYY-MM-DD'
                        }
                        return jsonify(response_json), response_json['code']
                elif k in ['id', 'comments']:
                    query = query.filter(getattr(FinancialReport, k).like(f"%{v}%"))
                else:
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
            'msg': '未找到符合条件的财务报表。'
        }
    return jsonify(response_json), response_json['code']


@fr_bp.route('/generate')
@permission_required(Permission.GENERATE_REPORTS)
def generate_report():
    report = g.current_user.create_financial_report()
    db.session.add(report)
    db.session.commit()
    task = current_app.celery.send_task('app.fr_init_async', args=[report.id])
    response_json = {'success': True, 'code': 200, 'task_id': task.id}
    return jsonify(response_json), response_json['code']


@fr_bp.route('/get-dl-link/<int:report_id>')
@permission_required(Permission.EXPORT_REPORTS)
def get_download_link(report_id):
    report = FinancialReport.query.get_or_404(report_id)
    download_url = url_for('api.v1.financial_report.download_report', token=report.generate_download_token())
    response_json = {'success': True, 'code': 200, 'url': download_url}
    return response_json, response_json['code']


@fr_bp.route('/dl/<token>')
def download_report(token):
    report = FinancialReport.verify_download_token(token)
    if report is None:
        abort(404)
    file_data = io.BytesIO(report.xlsx_data)
    return send_file(
        file_data,
        as_attachment=True,
        download_name=report.file_name,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@fr_bp.route('/rm/<int:report_id>', methods=['DELETE'])
@permission_required(Permission.DEL_REPORTS)
def remove_report(report_id):
    report = FinancialReport.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    response_json = {'success': True, 'code': 200}
    return jsonify(response_json), response_json['code']


@fr_bp.route('/update/<int:report_id>', methods=['PUT'])
@permission_required(Permission.GENERATE_REPORTS)
def update_fr(report_id):
    report = FinancialReport.query.get_or_404(report_id)
    if g.data is None:
        response_json = {
            'success': False,
            'code': 400,
            'msg': 'No data provided'
        }
    else:
        comments = g.data.get('comments')
        if comments is not None:
            report.comments = comments
            db.session.add(report)
            db.session.commit()
            response_json = {
                'success': True,
                'code': 200,
                'msg': '财务报表备注更新成功。'
            }
        else:
            response_json = {
                'success': False,
                'code': 400,
                'msg': 'No data provided'
            }
    return jsonify(response_json), response_json['code']
