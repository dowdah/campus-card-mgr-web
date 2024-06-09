from sqlalchemy import event
from sqlalchemy.orm import Session
from .models import User, Role, FinancialReport


def user_before_insert(mapper, connection, target):
    if target.alternative_id is None:
        target.alternative_id = User.generate_alternative_id()


def user_before_flush(session, flush_context, instances):
    for instance in session.new:
        if isinstance(instance, User) and instance.role is None:
            instance.role = Role.query.filter_by(default=True).first()


event.listen(User, 'before_insert', user_before_insert)
event.listen(Session, 'before_flush', user_before_flush)
