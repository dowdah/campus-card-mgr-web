from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import datetime
import random, string


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
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [
                Permission.LOGIN,
                Permission.SELF_CHANGE_PASSWORD,
                Permission.SELF_CHANGE_EMAIL,
                Permission.SELF_RECHARGE_CARD,
                Permission.SELF_CONSUME_CARD,
                Permission.SELF_REPORT_LOST_CARD
            ],
            'SchoolStaff': [
                Permission.LOGIN,
                Permission.SELF_CHANGE_PASSWORD,
                Permission.SELF_CHANGE_EMAIL,
                Permission.SELF_RECHARGE_CARD,
                Permission.SELF_CONSUME_CARD,
                Permission.SELF_REPORT_LOST_CARD,
                Permission.CANCEL_TRANSACTION,
                Permission.CHANGE_CARD_STATUS,
                Permission.RENEW_CARD,
                Permission.DEL_CARD,
                Permission.VIEW_USER_INFO,
                Permission.MODIFY_USER_INFO,
                Permission.DEL_USER,
                Permission.GENERATE_REPORTS,
                Permission.EXPORT_REPORTS,
                Permission.CHANGE_CARD_BALANCE
            ],
            'SiteOperator': [
                Permission.LOGIN,
                Permission.SELF_CHANGE_PASSWORD,
                Permission.SELF_CHANGE_EMAIL,
                Permission.SELF_RECHARGE_CARD,
                Permission.SELF_CONSUME_CARD,
                Permission.SELF_REPORT_LOST_CARD,
                Permission.CANCEL_TRANSACTION,
                Permission.CHANGE_CARD_STATUS,
                Permission.RENEW_CARD,
                Permission.DEL_CARD,
                Permission.VIEW_USER_INFO,
                Permission.MODIFY_USER_INFO,
                Permission.DEL_USER,
                Permission.GENERATE_REPORTS,
                Permission.EXPORT_REPORTS,
                Permission.CHANGE_CARD_BALANCE,
                Permission.BACKUP_DATA,
                Permission.RESTORE_DATA,
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
    GENERATE_REPORTS = 8192  # 生成报告
    EXPORT_REPORTS = 16384  # 导出报告
    MANAGE_PERMISSIONS = 32768  # 调整角色权限
    BACKUP_DATA = 65536  # 备份数据
    RESTORE_DATA = 131072  # 恢复数据
    CHANGE_CARD_BALANCE = 262144  # 更改卡余额
    OPERATOR = 524288  # 操作员权限


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    alternative_id = db.Column(db.String(64), unique=True, index=True)  # 用户的替代ID，用于生成token，初始化时自动生成
    student_id = db.Column(db.String(64), unique=True, index=True, nullable=False)  # 学号
    name = db.Column(db.String(64), unique=False, index=True, nullable=False)  # 姓名
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)  # 邮箱，用于二步验证
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # 创建时间
    password_hash = db.Column(db.String(128))  # 密码哈希值
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 用户的身份
    cards = db.relationship('Card', backref='user', lazy='dynamic', cascade='all, delete-orphan')  # 用户的一卡通
    confirmed = db.Column(db.Boolean, default=False)  # 是否已经通过邮箱验证
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')  # 用户的交易记录
    comments = db.Column(db.Text, nullable=True, default='')  # 备注(管理员添加)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()
        if self.alternative_id is None:
            self.alternative_id = User.generate_alternative_id()

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
        return self.cards.order_by(Card.created_at.desc()).all()

    @property
    def all_transaction_list(self):
        return self.transactions.order_by(Transaction.created_at.desc()).all()

    @property
    def latest_transaction_list(self):
        # 因为动张记录可能会很多，所以只返回最新的5条
        return self.transactions.order_by(Transaction.created_at.desc()).limit(5).all()

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
            'role': self.role.name,
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


class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    _balance = db.Column(db.Float, default=0.0)  # 卡片余额，单位为元
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    transactions = db.relationship('Transaction', backref='card', lazy='dynamic', cascade='all, delete-orphan')  # 卡片的交易记录
    is_banned = db.Column(db.Boolean, default=False)  # 是否被禁用
    is_lost = db.Column(db.Boolean, default=False)  # 是否被挂失
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # 创建时间
    expires_at = db.Column(db.DateTime, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=4 * 365))
    # 卡片有效期，默认为4年

    def __repr__(self):
        return '<Card %r>' % self.id

    @property
    def formatted_created_at(self):
        return self.created_at.strftime(OUTPUT_TIME_FORMAT)

    @property
    def formatted_expires_at(self):
        return self.expires_at.strftime(OUTPUT_TIME_FORMAT)

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
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

    @property
    def is_expired(self):
        return self.expires_at < datetime.datetime.utcnow()

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
        return True

    @property
    def all_transaction_list(self):
        return self.transactions.order_by(Transaction.created_at.desc()).all()

    @property
    def latest_transaction_list(self):
        # 因为动张记录可能会很多，所以只返回最新的5条
        return self.transactions.order_by(Transaction.created_at.desc()).limit(5).all()

    def to_json(self, include_related=True):
        json_card = {
            'id': self.id,
            'balance': '%.2f' % self.balance,
            'status': self.status,
            'created_at': self.formatted_created_at,
            'expires_at': self.formatted_expires_at,
            'is_active': self.is_active,
            'is_lost': self.is_lost,
            'is_expired': self.is_expired
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
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    comments = db.Column(db.Text, nullable=True, default='')

    def __repr__(self):
        return f'<Transaction {self.id}>'

    @property
    def formatted_created_at(self):
        return self.created_at.strftime(OUTPUT_TIME_FORMAT)

    def cancel(self):
        offset = -self.amount
        if offset > 0:
            self.card.recharge(offset, record=False)
            self.canceled = True
            db.session.add(self)
        else:
            self.card.consume(-offset, record=False)
            self.canceled = True
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
            'current_balance': '%.2f' % self.current_balance
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
    report_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    comments = db.Column(db.Text, nullable=True, default='')

    def __repr__(self):
        return f'<FinancialReport {self.id}>'
