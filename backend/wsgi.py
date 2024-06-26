import os
import click
from flask_migrate import Migrate
from app import create_app, db, mail
from app.models import User, Role, Card, Transaction, FinancialReport, Permission


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
celery = app.celery


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, mail=mail, Role=Role, Card=Card, Transaction=Transaction,
                FinancialReport=FinancialReport, Permission=Permission)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    # Run the unit tests.
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
