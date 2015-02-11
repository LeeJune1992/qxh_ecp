#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os.path
from datetime import datetime
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask.ext.script import Manager
from app import create_app
from settings.constants import  *
from global_settings import DMD_ID
from utils.memcached import cache

_app = create_app()
manager = Manager(_app)

from extensions import db

from core import models
from analytics.models import *

@manager.command
def jiexian():
    '''init data'''
    _conn = db.engine.raw_connection()
    try:
        cursor = _conn.cursor()
        cursor.execute('call jiexian()')
        print 'jiexian report success.'
    finally:
        _conn.close()

if __name__ == "__main__":
    manager.run()