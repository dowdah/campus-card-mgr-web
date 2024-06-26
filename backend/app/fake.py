from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Card, Role
from time import sleep
from alive_progress import alive_bar


def users(count=20):
    print("Making users...")
    fake = Faker()
    i = 0
    with alive_bar(count) as bar:
        while i < count:
            u = User(email=fake.email(),
                     name=fake.name(),
                     student_id=fake.random_int(min=2300160000, max=2300300000),
                     password='666666',
                     confirmed=True,
                     created_at=fake.date_time_this_year(),
                     comments='由 fake.py 生成的随机数据'
                     )
            db.session.add(u)
            try:
                db.session.commit()
                i += 1
            except IntegrityError:
                db.session.rollback()
            bar()


def cards():
    print("Making cards...")
    fake = Faker()
    user_list = User.query.all()
    with alive_bar(len(user_list)) as bar:
        for user in user_list:
            if len(user.card_list) > 1:
                continue
            for i in range(0, randint(1, 2)):
                created_at = fake.date_time_this_year()
                expires_at = created_at.replace(year=created_at.year + 4)
                c = Card(user=user,
                         created_at=created_at,
                         expires_at=expires_at)
                db.session.add(c)
            bar()
        db.session.commit()
    with alive_bar(len(Card.query.all())) as bar:
        for card in Card.query.all():
            card.balance = randint(0, 1000)
            bar()


def transactions():
    print("Making transacations...")
    fake = Faker()
    card_list = Card.query.all()
    with alive_bar(len(card_list)) as bar:
        for card in card_list:
            for i in range(0, randint(14, 40)):
                offset = randint(-card.balance, 100)
                card.balance += offset
            bar()


def main(count=20):
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    admin = Role.query.filter_by(name='管理员').first()
    user = Role.query.filter_by(name='普通用户').first()
    u_1 = User(email='x@dowdah.com', name='张天宇', student_id=2300160426, password='666666', confirmed=True, role=admin)
    db.session.add(u_1)
    u_2 = User(email='strangecarhead@foxmail.com', name='张天宇', student_id=2300160427, password='666666', confirmed=True, role=user)
    db.session.add(u_2)
    u_unconfirmed = User(email='dowdah@qq.com', name='张天宇', student_id=2300160428, password='666666', confirmed=False, role=user)
    db.session.add(u_unconfirmed)
    db.session.commit()
    u_1.create_card()
    u_2.create_card()
    users(count=count)
    cards()
    transactions()
