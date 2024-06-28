from flask import current_app, render_template
from app import db
from app.models import FinancialReport
from flask_mail import Message
from . import mail


celery = current_app.celery


@celery.task(name='app.fr_init_async', bind=True)
def fr_init_async(self, fr_id):
    d = dict()
    try:
        fr_obj = FinancialReport.query.get(fr_id)
        fr_obj.generate_json_data()
        fr_obj.generate_xlsx_data()
        db.session.add(fr_obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.delete(FinancialReport.query.get(fr_id))
        db.session.commit()
        d['success'] = False
        d['msg'] = str(e)
    else:
        d['success'] = True
        d['msg'] = 'Report generated successfully'
    return d


@celery.task(name='app.send_email', bind=True)
def send_email(self, recipients, subject, template, **kwargs):
    msg = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=current_app.config['MAIL_SENDER'], recipients=recipients)
    msg.html = render_template(template, **kwargs)
    try:
        mail.send(msg)
    except Exception as e:
        self.retry(exc=e)
