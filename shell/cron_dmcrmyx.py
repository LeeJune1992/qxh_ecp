#coding=utf-8
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
reload(sys) 
sys.setdefaultencoding("utf-8")
import  datetime

from global_settings import SQLALCHEMY_DATABASE_URI,SQLALCHEMY_BINDS
from collections import defaultdict,deque
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import User,User_Phone
import MySQLdb
if __name__ == '__main__':
    print '[CRON]%s -> %s'%(__file__,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    _now = datetime.datetime.now()
    _yesterday = _now+datetime.timedelta(days=-1)
    _yesterday2 = _now+datetime.timedelta(days=-2)

    _date = _yesterday.strftime('%Y-%m-%d')
    _date2 = _yesterday2.strftime('%Y-%m-%d')
    db = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=240, echo=False)
    conn = db.connect()
    sqls = []
    try:
        sql = """SELECT * FROM qxhdm_user WHERE is_valid>0 and valid_time>'%s'"""%_date
        print sql
        users = conn.execute(sql)
        print 'ok'
        for user in users:
            sql = """update qxhdm_user set is_valid='%s',valid_time='%s' where id='%s'"""%(user.is_valid,user.valid_time,user.id)
            sqls.append(sql)
        print 'WRITE OK.'
    except Exception,e:
        print 'WRITE error:%s'%e
    finally:
        conn.close()
    
    if sqls:
        db = create_engine(SQLALCHEMY_BINDS['dmcrm'], pool_recycle=240, echo=False)
        conn = db.connect()

        try:
            for sql in sqls:
                print sql
                dmusers = conn.execute(sql)
            print 'DOWN OK.'
        except Exception,e:
            print 'DOWN error:%s'%e
        finally:
            conn.close()

#
#            user.operator_id = 1
#            user.name = dmuser.name
#            user.phone = dmuser.phone
#            user.phone2 = dmuser.phone2
#            user.gender = dmuser.gender
#            user.ages = dmuser.ages
#            user.is_new = dmuser.is_new
#            user.disease = dmuser.disease
#            user.fugou = dmuser.fugou
#            user.remark = dmuser.remark            
#            user.purchases = purchases
#            user.qxhdm_user_id = dmuser.id