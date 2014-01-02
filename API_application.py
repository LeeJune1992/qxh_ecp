# -*- coding: utf-8 -*-
import sys
import os.path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from flask import Flask
from extensions import db
from core.API import api


def configure_logging(app):
    """Configure file(info) and email(error) logging."""
    import logging
    from logging.handlers import SMTPHandler

    app.logger.setLevel(logging.INFO)
    file_handler = logging.handlers.RotatingFileHandler(os.path.join(app.config['LOG_PATH'], 'ecp.log'), maxBytes=100000, backupCount=10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s](%(levelname)s) %(message)s  [%(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)


def create_app():
    _app = Flask(__name__)
    _app.config.from_pyfile('global_settings.py')
    _app.config.from_object('settings.constants')
    db.init_app(_app)


    configure_logging(_app)
    _app.register_blueprint(api)
    return _app


app = create_app()

if __name__ == '__main__':
    app.run('0.0.0.0')