from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Card


def users(count=20):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='123456',
                 confirmed=True,
                 created_at=fake.date_time_this_year())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def cards():
    fake = Faker()
    user_list = User.query.all()
    for user in user_list:
        if len(user.get_cards()) > 0:
            continue
        created_at = fake.date_time_this_year()
        expires_at = created_at.replace(year=created_at.year + 4)
        c = Card(user_id=user.id,
                 balance=randint(0, 200),
                 created_at=created_at,
                 expires_at=expires_at)
        db.session.add(c)
    db.session.commit()
