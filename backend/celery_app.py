from celery import Celery

def make_celery(app=None):
    celery = Celery(
        app.import_name if app else 'celery_app',
        backend='redis://redis:6379/0',
        broker='redis://redis:6379/0'
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            if app:
                with app.app_context():
                    return self.run(*args, **kwargs)
            else:
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    if app:
        celery.conf.update(app.config)
    return celery

celery = make_celery()

@celery.task(name='app.reverse')
def reverse(string):
    return string[::-1]
