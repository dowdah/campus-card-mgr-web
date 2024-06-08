from flask import Flask
from config import config
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mail = Mail()


def not_found_error(e):
    return {'success': False, 'code': 404, 'msg': 'Not found'}, 404


def method_not_allowed_error(e):
    return {'success': False, 'code': 405, 'msg': 'Method not allowed'}, 405


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(405, method_not_allowed_error)
    config[config_name].init_app(app)
    mail.init_app(app)
    db.init_app(app)
    from celery_app import celery
    celery.conf.update(app.config)
    app.celery = celery
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        # 导入模型和事件监听器
        from . import models
        from . import listeners

    @app.context_processor
    def inject_variables():
        return {'site_name': app.config['SITE_NAME']}

    return app
