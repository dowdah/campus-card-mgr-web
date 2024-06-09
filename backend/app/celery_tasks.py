from flask import current_app
from app import db
from app.models import FinancialReport


celery = current_app.celery


@celery.task(name='app.reverse')
def reverse(string):
    return string[::-1]


@celery.task(name='app.fr_init_async', bind=True)
def fr_init_async(self, fr_id):
    try:
        fr_obj = FinancialReport.query.get(fr_id)
        fr_obj.generate_json_data()
        fr_obj.generate_xlsx_data()
        db.session.add(fr_obj)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        db.session.delete(FinancialReport.query.get(fr_id))
        db.session.commit()
        return False
