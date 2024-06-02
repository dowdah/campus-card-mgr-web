from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import datetime


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

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
        self. permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [
                Permission.VIEW_BALANCE,
                Permission.VIEW_TRANSACTIONS,
                Permission.RECHARGE_CARD,
                Permission.REPORT_LOST_CARD
            ],
            'SchoolStaff': [
                Permission.VIEW_BALANCE,
                Permission.VIEW_TRANSACTIONS,
                Permission.RECHARGE_CARD,
                Permission.REPORT_LOST_CARD,
                Permission.MODIFY_USER_INFO,
                Permission.VIEW_USER_INFO,
                Permission.GENERATE_REPORTS,
                Permission.EXPORT_REPORTS
            ],
            'SiteOperator': [
                Permission.VIEW_BALANCE,
                Permission.VIEW_TRANSACTIONS,
                Permission.RECHARGE_CARD,
                Permission.REPORT_LOST_CARD,
                Permission.MODIFY_USER_INFO,
                Permission.DELETE_USER_INFO,
                Permission.VIEW_USER_INFO,
                Permission.GENERATE_REPORTS,
                Permission.EXPORT_REPORTS,
                Permission.BACKUP_DATA,
                Permission.RESTORE_DATA,
                Permission.VIEW_SYSTEM_LOGS,
                Permission.MANAGE_PERMISSIONS,
                Permission.OPERATOR
            ]
        }
        default_role = 'User'
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
    VIEW_BALANCE = 1           # 查看余额
    VIEW_TRANSACTIONS = 2      # 查看交易记录
    RECHARGE_CARD = 4          # 充值卡片
    REPORT_LOST_CARD = 8       # 挂失卡片
    MODIFY_USER_INFO = 16      # 修改用户信息
    DELETE_USER_INFO = 32      # 删除用户信息
    VIEW_USER_INFO = 64        # 查看用户信息
    GENERATE_REPORTS = 128     # 生成财务报表
    EXPORT_REPORTS = 256       # 导出财务报表
    BACKUP_DATA = 512          # 数据备份
    RESTORE_DATA = 1024        # 数据恢复
    VIEW_SYSTEM_LOGS = 2048    # 查看系统日志
    MANAGE_PERMISSIONS = 4096  # 权限管理
    OPERATOR = 8192            # 后台操作员


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    alternative_id = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    cards = db.relationship('Card', backref='user', lazy='dynamic')
    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % self.username

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

    def get_id(self):
        return self.alternative_id

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

    def get_cards(self):
        return self.cards.all()

    def get_card(self, card_id):
        return self.cards.filter_by(id=card_id).first()

    def to_json(self):
        json_user = {
            'username': self.username,
            'alternative_id': self.alternative_id,
            'created_at': self.created_at,
            'id': self.id,
            'email': self.email,
            'role': self.role.name,
            'confirmed': self.confirmed,
            'cards': [card.to_json() for card in self.get_cards()]
        }
        return json_user


class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)  # 卡片余额，单位为元
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(64), default='active')  # 卡片状态，active: 正常，lost: 挂失, inactive: 失效
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=4 * 365))
    # 卡片有效期，默认为4年

    def __repr__(self):
        return '<Card %r>' % self.id

    def recharge(self, amount):
        if amount > 0:
            self.balance += amount
            db.session.add(self)
            return True
        return False

    def report_lost(self):
        self.status = 'lost'
        db.session.add(self)
        return True

    def deactivate(self):
        self.status = 'inactive'
        db.session.add(self)
        return True

    def activate(self):
        self.status = 'active'
        db.session.add(self)
        return True

    def consume(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            db.session.add(self)
            return True
        return False

    def is_active(self):
        return self.status == 'active'

    def is_lost(self):
        return self.status == 'lost'

    def is_inactive(self):
        return self.status == 'inactive'

    def is_expired(self):
        return self.expires_at < datetime.datetime.utcnow()

    def renew(self, days):
        self.expires_at += datetime.timedelta(days=days)
        db.session.add(self)
        return True

    def get_owner(self):
        return User.query.get(self.user_id)

    def to_json(self):
        json_card = {
            'owner_username': self.get_owner().username,
            'id': self.id,
            'balance': self.balance,
            'status': self.status,
            'created_at': self.created_at,
            'expires_at': self.expires_at
        }
        return json_card


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.id} - {self.amount}>'


class FinancialReport(db.Model):
    __tablename__ = 'financial_reports'
    id = db.Column(db.Integer, primary_key=True)
    report_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<FinancialReport {self.id}>'
