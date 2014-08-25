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

from utils.memcached import cache

_app = create_app()
manager = Manager(_app)

from extensions import db

from core.models import User,User_Phone
import pycurl
from StringIO import StringIO
from global_settings import DMURL
from flask import json
@manager.command
def getdmuser():
    html = StringIO()
    url = r'%sgetuser'%DMURL
    print datetime.now()
    print url
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.SSL_VERIFYHOST, False)
    c.setopt(pycurl.SSL_VERIFYPEER, False)
    c.setopt(pycurl.WRITEFUNCTION, html.write)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.perform()
    
    ll = str(html.getvalue())
    users = json.loads(ll)
    for u in users:
        user = User()
        p = User_Phone.query.filter(db.or_(User_Phone.phone == u['phone'],User_Phone.phone == u['phone2'])).first()
        if p:
            user = User.query.get_or_404(p.user_id)
            user.operator_id = 1
            user.origin = 18
            #user.assign_operator_id = 1
            purchases = u['name']+u'于'+u['gmdate']+u' 在 '+u['gmaddress']+u' 购买了大盒'+str(u['gmbigcount'])+u'盒，小盒'+str(u['gmsmallcount'])+u'盒,备注：'+u['remark']+u',电话：'+u['phone']+','+u['phone2']+u',年龄：'+str(u['ages'])+u',性别：'+u['gender']
            user.purchases = purchases
            user.qxhdm_user_id = u['id']

            db.session.add(user)

        else:            
            user.operator_id = 1
            user.origin = 18
            #user.assign_operator_id = 1
            user.name = u['name']
            user.phone = u['phone']
            user.phone2 = u['phone2']
            user.gender = u['gender']
            user.ages = u['ages']
            user.is_new = u['is_new']
            user.disease = u['disease']
            user.fugou = u['fugou']
            user.remark = u['remark']
            purchases = u['gmdate']+u' 在 '+u['gmaddress']+u' 购买了大盒'+str(u['gmbigcount'])+u'盒，小盒'+str(u['gmsmallcount'])+u'盒'
            user.purchases = purchases
            user.qxhdm_user_id = u['id']

            db.session.add(user)
            db.session.flush()
            db.session.add(User_Phone.add_phone(user.user_id,user.phone))
            if user.phone2:
                db.session.add(User_Phone.add_phone(user.user_id,user.phone2))

        url = r'%supdateuser?id=%s&user_id=%s'%(DMURL,u['id'],user.user_id)
        print url
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.SSL_VERIFYHOST, False)
        c.setopt(pycurl.SSL_VERIFYPEER, False)
        c.setopt(pycurl.WRITEFUNCTION, html.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.perform()

        db.session.commit()

#@manager.command
#def dmuserphone():
#    users = User.query.filter(User.qxhdm_user_id > 0)
#    for user in users:
#        print user.user_id
#        db.session.add(User_Phone.add_phone(user.user_id,user.phone))
#    db.session.commit()


if __name__ == "__main__":
    manager.run()