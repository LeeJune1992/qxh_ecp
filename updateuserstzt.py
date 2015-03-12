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

_app = create_app()
manager = Manager(_app)

from extensions import db

from core.models import User
from flask import json
@manager.command
def update():
    print 'begin:'+datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    users = User.query.filter()#(User.user_id == 68)#.first()
    print 'select:'+datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #print users.entries
    for user in users:
        #print user.user_id
        #print user.entries
        try:
            if user.entries:
                u = json.loads(user.entries)
                sts = u['BODY']
                orgin = []
                orgina = ''
                orginb = ''
                orginc = ''
                orgind = ''
                orgine = ''
                history = ''
                #print len(sts)
                if len(sts)>0:
                    for st in sts:
                        if st.find('Z') == -1:
                            orgin.append(st)
                        if st.find('A') > -1:
                            orgina+=sts[st]['c3']+sts[st]['v']+' '
                        if st.find('B') > -1:
                            orginb+=sts[st]['c3']+sts[st]['v']+' '
                        if st.find('C') > -1:
                            orginc+=sts[st]['c3']+sts[st]['v']+' '
                        if st.find('D') > -1:
                            orgind+=sts[st]['c3']+sts[st]['v']+' '
                        if st.find('E') > -1:
                            orgine+=sts[st]['c3']+sts[st]['v']+' '
                        if st.find('Z') > -1:
                            history=sts[st]['v']+' '
                    #print orgin
                    user.orgin = orgin
                    #return 'ok3'
                    user.orgina = orgina
                    user.orginb = orginb
                    user.orginc = orginc
                    user.orgind = orgind
                    user.orgine = orgine
                    user.history = history
                    db.session.add(user)
        except Exception,e:
            print user.user_id
            print 'error:'+datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print 'update:'+datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    print 'submit:'+datetime.now().strftime('%Y-%m-%d %H:%M:%S')


#    for user in users:
#        if User_Phone.query.filter(User_Phone.phone == user.phone).first():
#            pass
#        else:
#            print user.user_id
#            db.session.add(User_Phone.add_phone(user.user_id,user.phone))
#    db.session.commit()


if __name__ == "__main__":
    manager.run()