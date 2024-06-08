from flask import jsonify, request, g, abort, current_app, Blueprint
from ...models import User, Permission, Card, Transaction, FinancialReport
from ... import db
from ...decorators import permission_required


fr_bp = Blueprint('financial_report', __name__)

