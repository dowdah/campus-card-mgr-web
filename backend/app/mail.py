from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from time import localtime
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """
    :param to: a list of email address
    :param subject: subject of the email
    :param template: template of the email
    :return:
    """
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=to)
    # msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template, current_year=localtime().tm_year, site_name=app.config['SITE_NAME'].title(),
                               **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_email_without_template(to, subject, content):
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=to)
    msg.body = content
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
