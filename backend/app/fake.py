from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Card, Role


def users(count=20):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 name=fake.name(),
                 student_id=fake.random_int(min=2300160000, max=2300300000),
                 password='666666',
                 confirmed=True,
                 created_at=fake.date_time_this_year(),
                 comments='Generated by fake.py'
                 )
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
        if len(user.card_list) > 0:
            continue
        created_at = fake.date_time_this_year()
        expires_at = created_at.replace(year=created_at.year + 4)
        c = Card(user=user,
                 created_at=created_at,
                 expires_at=expires_at)
        db.session.add(c)
    db.session.commit()
    for card in Card.query.all():
        card.balance = randint(0, 1000)
        db.session.add(card)
    db.session.commit()


def main():
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    school_staff = Role.query.filter_by(name='SchoolStaff').first()
    site_operator = Role.query.filter_by(name='SiteOperator').first()
    u_1 = User(email='x@dowdah.com', name='张天宇', student_id=2300160426, password='666666', confirmed=True, role=site_operator)
    db.session.add(u_1)
    u_2 = User(email='1534887783@qq.com', name='乔', student_id=2300114514, password='666666', confirmed=True, role=school_staff)
    db.session.add(u_2)
    db.session.commit()
    u_1.create_card()
    u_2.create_card()
    users()
    cards()
