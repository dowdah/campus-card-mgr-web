import datetime
import random
import string
import json
import io
import pandas as pd

from flask import current_app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.hybrid import hybrid_property

from . import db

OUTPUT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return '<Role %r>' % self.name

    # SQLAlchemy 默认把这个字段的值设为None，因此我添加了一个类构造函
    # 数，在未给构造函数提供参数时，把这个字段的值设为0

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        if self.permissions & Permission.OPERATOR == Permission.OPERATOR:
            # 如果是操作员，那么拥有所有权限
            return True
        else:
            return self.permissions & perm == perm

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'default': self.default,
            'permissions': self.permissions
        }

    @staticmethod
    def insert_roles():
        roles = {
            '普通用户': [
                Permission.LOGIN,
                Permission.SELF_CHANGE_PASSWORD,
                Permission.SELF_CHANGE_EMAIL,
                Permission.SELF_RECHARGE_CARD,
                Permission.SELF_CONSUME_CARD,
                Permission.SELF_REPORT_LOST_CARD
            ],
            '管理员': [
                Permission.OPERATOR
            ]
        }
        default_role = '普通用户'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class Permission:
    LOGIN = 1  # 登录权限
    SELF_CHANGE_PASSWORD = 2  # 自己修改密码
    SELF_CHANGE_EMAIL = 4  # 自己修改邮箱
    SELF_RECHARGE_CARD = 8  # 自己充值卡
    SELF_CONSUME_CARD = 16  # 自己消费卡
    SELF_REPORT_LOST_CARD = 32  # 自己挂失卡
    CANCEL_TRANSACTION = 64  # 撤销交易
    CHANGE_CARD_STATUS = 128  # 更改卡状态
    RENEW_CARD = 256  # 续卡
    DEL_CARD = 512  # 删除卡
    VIEW_USER_INFO = 1024  # 查看用户信息
    MODIFY_USER_INFO = 2048  # 修改用户信息
    DEL_USER = 4096  # 删除用户
    GENERATE_REPORTS = 8192  # 生成报告(包括编辑报告的备注)
    EXPORT_REPORTS = 16384  # 下载报告
    MANAGE_PERMISSIONS = 32768  # 调整角色权限
    BACKUP_DATA = 65536  # 备份数据
    RESTORE_DATA = 131072  # 恢复数据
    CHANGE_CARD_BALANCE = 262144  # 更改卡余额
    OPERATOR = 524288  # 最高权限
    ADD_USER = 1048576  # 添加用户
    DEL_REPORTS = 2097152  # 删除报告
    ADD_CARD = 4194304  # 添加卡

    @staticmethod
    def to_json():
        d = dict()
        for k, v in Permission.__dict__.items():
            if not k.startswith('__') and not callable(v) and isinstance(v, int):
                d[k] = v
        return d


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    alternative_id = db.Column(db.String(64), unique=True, index=True)  # 用户的替代ID，用于生成token，初始化时自动生成
    student_id = db.Column(db.String(64), unique=True, index=True, nullable=False)  # 学号
    name = db.Column(db.String(64), unique=False, index=True, nullable=False)  # 姓名
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)  # 邮箱，用于二步验证
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)  # 创建时间
    password_hash = db.Column(db.String(128))  # 密码哈希值
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 用户的身份
    cards = db.relationship('Card', backref='user', lazy='dynamic', cascade='all, delete-orphan')  # 用户的一卡通
    confirmed = db.Column(db.Boolean, default=False)  # 是否已经通过邮箱验证
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # 用户的交易记录
    comments = db.Column(db.Text, nullable=True, default='')  # 备注(管理员添加)
    financial_reports = db.relationship('FinancialReport', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # 管理员的财务报告

    def __repr__(self):
        return '<User %s(%s)>' % (self.name, self.student_id)

    @property
    def formatted_created_at(self):
        return self.created_at.strftime(OUTPUT_TIME_FORMAT)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'alternative_id': self.alternative_id})

    def validate_token(self, token, expiration=None):
        if expiration is None:
            expiration = current_app.config['EMAIL_TOKEN_EXPIRATION']
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'), max_age=expiration)
        except:
            return False
        if data.get('alternative_id') != self.alternative_id:
            return False
        return True

    def confirm(self, token):
        if self.validate_token(token):
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_operator(self):
        return self.can(Permission.OPERATOR)

    def generate_auth_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'alternative_id': self.alternative_id})

    @staticmethod
    def verify_auth_token(token, expiration=None):
        if expiration is None:
            expiration = current_app.config['API_TOKEN_EXPIRATION']
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'), max_age=expiration)
        except:
            return None
        user = User.query.filter_by(alternative_id=data.get('alternative_id')).first()
        if user:
            return user
        else:
            return None

    @staticmethod
    def generate_alternative_id(length=12):
        alternative_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        while User.query.filter_by(alternative_id=alternative_id).first() is not None:
            alternative_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return alternative_id

    @property
    def card_list(self):
        return self.cards.order_by(Card.id.desc()).all()

    @property
    def all_transaction_list(self):
        return self.transactions.order_by(Transaction.id.desc()).all()

    @property
    def latest_transaction_list(self):
        # 因为动张记录可能会很多，所以只返回最新的5条
        return self.transactions.order_by(Transaction.id.desc()).limit(5).all()

    def create_card(self):
        card = Card(user=self)
        db.session.add(card)
        db.session.commit()
        return card

    def to_json(self, include_sensitive=False, include_related=True):
        json_user = {
            'name': self.name,
            'alternative_id': self.alternative_id,
            'student_id': self.student_id,
            'created_at': self.formatted_created_at,
            'id': self.id,
            'email': self.email,
            'role': self.role.to_json(),
            'confirmed': self.confirmed
        }
        if include_related:
            related_json = {
                'cards': [card.to_json(include_related=False) for card in self.card_list],
                'latest_transactions': [transaction.to_json(include_related=False, include_sensitive=include_sensitive)
                                        for transaction in self.latest_transaction_list]
            }
            json_user.update(related_json)
        if include_sensitive:
            sensitive_json = {
                'comments': self.comments,
                'id': self.id
            }
            json_user.update(sensitive_json)
        return json_user

    def create_financial_report(self, comments=''):
        if self.can(Permission.GENERATE_REPORTS):
            report = FinancialReport(user=self, comments=comments)
            return report
        else:
            return None


class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    _balance = db.Column(db.Float, default=0.0)  # 卡片余额，单位为元
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    transactions = db.relationship('Transaction', backref='card', lazy='dynamic', cascade='all, delete-orphan')  # 卡片的交易记录
    is_banned = db.Column(db.Boolean, default=False)  # 是否被禁用
    is_lost = db.Column(db.Boolean, default=False)  # 是否被挂失
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)  # 创建时间
    expires_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now() + datetime.timedelta(days=4 * 365))
    # 卡片有效期，默认为4年

    def __repr__(self):
        return '<Card %r>' % self.id

    @property
    def formatted_created_at(self):
        return self.created_at.strftime(OUTPUT_TIME_FORMAT)

    @property
    def formatted_expires_at(self):
        return self.expires_at.strftime(OUTPUT_TIME_FORMAT)

    @hybrid_property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if self._balance is None:
            self._balance = 0.0
        if value >= 0:
            offset = value - self._balance
            if offset != 0:
                comments = '由系统做出的更改'
                t = Transaction(user=self.user, card=self, amount=offset, comments=comments,
                                original_balance=self._balance, current_balance=value)
                db.session.add(t)
            self._balance = value
            db.session.add(self)
            db.session.commit()
        else:
            raise ValueError('Balance must be non-negative.')

    def recharge(self, amount, comments='', record=True):
        if amount > 0:
            if record:
                t = Transaction(user=self.user, card=self, amount=amount, comments=comments,
                                original_balance=self.balance, current_balance=self.balance + amount)
                db.session.add(t)
            self._balance += amount
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def consume(self, amount, comments='', record=True):
        if 0 < amount <= self.balance:
            if record:
                t = Transaction(user=self.user, card=self, amount=-amount, comments=comments,
                                original_balance=self.balance, current_balance=self.balance - amount)
                db.session.add(t)
            self._balance -= amount
            db.session.add(self)
            db.session.commit()
            return True
        return False

    @property
    def is_active(self):
        return not (self.is_banned or self.is_expired or self.is_lost)

    @hybrid_property
    def is_expired(self):
        return self.expires_at < datetime.datetime.now()

    @property
    def status(self):
        status_list = []
        if self.is_banned:
            status_list.append('禁用')
        if self.is_lost:
            status_list.append('已挂失')
        if self.is_expired:
            status_list.append('过期')
        return ','.join(status_list) if status_list else '正常'

    def renew(self, days):
        self.expires_at += datetime.timedelta(days=days)
        db.session.add(self)
        db.session.commit()
        return True

    @property
    def all_transaction_list(self):
        return self.transactions.order_by(Transaction.id.desc()).all()

    @property
    def latest_transaction_list(self):
        # 因为动账记录可能会很多，所以只返回最新的5条
        return self.transactions.order_by(Transaction.id.desc()).limit(5).all()

    def to_json(self, include_related=True):
        json_card = {
            'id': self.id,
            'balance': '%.2f' % self.balance,
            'status': self.status,
            'created_at': self.formatted_created_at,
            'expires_at': self.formatted_expires_at,
            'is_active': self.is_active,
            'is_lost': self.is_lost,
            'is_expired': self.is_expired,
            'is_banned': self.is_banned
        }
        if include_related:
            related_json = {
                'latest_transactions': [transaction.to_json(include_related=False)
                                        for transaction in self.latest_transaction_list],
                'user': self.user.to_json(include_related=False)
            }
            json_card.update(related_json)
        return json_card


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    original_balance = db.Column(db.Float, nullable=True)
    current_balance = db.Column(db.Float, nullable=True)
    is_canceled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    comments = db.Column(db.Text, nullable=True, default='')

    def __repr__(self):
        return f'<Transaction {self.id}>'

    @property
    def formatted_created_at(self):
        return self.created_at.strftime(OUTPUT_TIME_FORMAT)

    @property
    def status(self):
        return '已撤销' if self.is_canceled else '正常'

    def cancel(self):
        offset = -self.amount
        if offset > 0:
            self.card.recharge(offset, record=False)
            self.is_canceled = True
        else:
            if self.card.consume(-offset, record=False):
                self.is_canceled = True
            else:
                return False
        db.session.add(self)
        db.session.commit()
        return True

    def to_json(self, include_related=True, include_sensitive=False):
        json_transaction = {
            'id': self.id,
            'amount': '%.2f' % self.amount,
            'created_at': self.formatted_created_at,
            'is_canceled': self.is_canceled,
            'original_balance': '%.2f' % self.original_balance,
            'current_balance': '%.2f' % self.current_balance,
            'card_id': self.card_id,
            'status': self.status
        }
        if include_related:
            related_json = {
                'user': self.user.to_json(include_related=False),
                'card': self.card.to_json(include_related=False)
            }
            json_transaction.update(related_json)
        if include_sensitive:
            sensitive_json = {
                'comments': self.comments
            }
            json_transaction.update(sensitive_json)
        return json_transaction


class FinancialReport(db.Model):
    __tablename__ = 'financial_reports'
    id = db.Column(db.Integer, primary_key=True)
    json_data = db.Column(LONGTEXT, nullable=True)
    xlsx_data = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now, index=True, nullable=False)
    xlsx_expiration = db.Column(db.Interval, nullable=True, default=datetime.timedelta(days=7))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_income = db.Column(db.Float, nullable=True)
    total_expenses = db.Column(db.Float, nullable=True)
    net_growth = db.Column(db.Float, nullable=True)
    comments = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<FinancialReport {self.id}>'

    @property
    def formatted_created_at(self):
        return self.created_at.strftime(OUTPUT_TIME_FORMAT)

    @hybrid_property
    def is_xlsx_expired(self):
        return self.xlsx_expiration is not None and self.created_at + self.xlsx_expiration < datetime.datetime.now()

    @property
    def file_name(self):
        return f'fr_{self.id}.xlsx'

    def to_json(self):
        # json_data 和 xlsx_data 字段往往过于庞大，因此不在这里返回，需要单独获取
        return {
            'id': self.id,
            'created_at': self.formatted_created_at,
            'user': self.user.to_json(include_related=False),
            'total_income': f'{self.total_income:.2f}',
            'total_expenses': f'{self.total_expenses:.2f}',
            'net_growth': f'{self.net_growth:.2f}',
            'is_xlsx_expired': self.is_xlsx_expired,
            'comments': self.comments
        }

    def generate_json_data(self):
        # 从Transactions表中提取数据
        transactions = Transaction.query.all()
        total_income = sum(t.amount for t in transactions if t.amount > 0 and not t.is_canceled)
        total_expenses = sum(-t.amount for t in transactions if t.amount < 0 and not t.is_canceled)
        net_growth = total_income - total_expenses
        # 生成结构化的report_data
        transactions_data = [
            {
                'id': t.id,
                'amount': t.amount,
                'created_at': t.created_at.strftime(OUTPUT_TIME_FORMAT),
                'status': '已撤销' if t.is_canceled else '正常',
                'original_balance': t.original_balance,
                'current_balance': t.current_balance,
                'comments': t.comments,
                'student_id': t.user.student_id
            }
            for t in transactions
        ]

        report_data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_growth': net_growth,
            'transactions': transactions_data
        }

        # 将report_data转换为JSON格式并存储在数据库中
        self.json_data = json.dumps(report_data, ensure_ascii=False)
        self.total_income = total_income
        self.total_expenses = total_expenses
        self.net_growth = net_growth

    def generate_xlsx_data(self):
        # 从json_data中提取数据
        report_data = json.loads(self.json_data)
        transactions_data = report_data['transactions']
        df = pd.DataFrame(transactions_data)
        # 生成xlsx_data
        df_transactions = pd.DataFrame(transactions_data)
        df_transactions.rename(columns={
            'id': '交易ID',
            'amount': '金额',
            'created_at': '交易时间',
            'status': '状态',
            'original_balance': '卡片原余额',
            'current_balance': '卡片交易后余额',
            'comments': '备注',
            'student_id': '学生ID'
        }, inplace=True)
        summary_data = {
            '总收入': [report_data['total_income']],
            '总支出': [report_data['total_expenses']],
            '净增长': [report_data['net_growth']]
        }
        df_summary = pd.DataFrame(summary_data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_transactions.to_excel(writer, sheet_name='交易', index=False)
            df_summary.to_excel(writer, sheet_name='总览', index=False)
        buffer.seek(0)
        self.xlsx_data = buffer.read()

    def generate_download_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_download_token(token, expiration=None):
        if expiration is None:
            expiration = current_app.config['FR_TOKEN_EXPIRATION']
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'), max_age=expiration)
        except:
            return None
        if data.get('id') is not None:
            report = FinancialReport.query.get(data.get('id'))
            if report is not None:
                return report
        return None
