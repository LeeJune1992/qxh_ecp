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
    db = create_engine(SQLALCHEMY_BINDS['dmcrm'], pool_recycle=240, echo=False)
    conn = db.connect()
    filename = '/data/crmtest/'+_yesterday2.strftime('%Y%m%d')
    #filename = 'd:\\'+_yesterday2.strftime('%Y%m%d')
    print filename
    try:
        sql = """SELECT * INTO OUTFILE '%s.txt' FIELDS TERMINATED BY ',' FROM qxhdm_user WHERE created > '%s' and created < '%s'"""%(filename,_date2,_date)
        print sql
        conn.execute(sql)
        print 'DOWN OK.'
    except Exception,e:
        print 'DOWN error:%s'%e
    finally:
        conn.close()

    db = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=240, echo=False)
    conn = db.connect()
    conn.execute("""LOAD DATA INFILE '%s.txt' INTO TABLE qxhdm_user FIELDS TERMINATED BY ','"""%filename)

    try:
        sql = """SELECT * FROM qxhdm_user WHERE created > '%s' and created < '%s'"""%(_date2,_date)
        #print sql
        dmusers = conn.execute(sql)
        print 'ok'
        for dmuser in dmusers:
            purchases = str(dmuser.gmdate)+u' 在 '+str(dmuser.gmaddress)+u' 购买了大盒'+str(dmuser.gmbigcount)+u'盒，小盒'+str(dmuser.gmsmallcount)+u'盒'
            sql = """select distinct(user_id) from user_phone where phone='%s' or phone='%s'"""%(dmuser.phone,dmuser.phone2)
            print sql
            phones = conn.execute(sql)
            user_id = 0
            for p in phones:
                user_id = p.user_id
            
            if user_id:
                sql = u"""update user set operator_id=1,assign_operator_id=1,join_time=now(),
                purchases='%s',qxhdm_user_id='%s',is_new='%s',disease='%s',fugou='%s',purchases='%s' where user_id='%s'"""%(purchases,dmuser.id,dmuser.is_new,dmuser.disease,dmuser.fugou,(purchases+u',备注：'+dmuser.remark+u',电话：'+dmuser.phone+dmuser.phone2+u',姓名：'+dmuser.name+u',年龄：'+str(dmuser.ages)+u',性别：'+dmuser.gender),user_id)
            else:
                sql = u"""insert into user (operator_id,assign_operator_id,join_time,name,phone,phone2,gender,ages,is_new,disease,fugou,remark,purchases,qxhdm_user_id) values
            (1,1,now(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
            """%(dmuser.name,dmuser.phone,dmuser.phone2,dmuser.gender,dmuser.ages,dmuser.is_new,dmuser.disease,dmuser.fugou,dmuser.remark,purchases,dmuser.id)
            print sql
            conn.execute(sql)
        sql = """SELECT qxhdm_user_id,user_id FROM user where qxhdm_user_id in (SELECT id FROM qxhdm_user WHERE created > '%s' and created < '%s')"""%(_date2,_date)
        gxusers = conn.execute(sql)
        print sql
        for user in gxusers:
            sql = """update qxhdm_user set user_id='%s' where id='%s'"""%(user.user_id,user.qxhdm_user_id)
            print sql
            conn.execute(sql)
        print 'WRITE OK.'
    except Exception,e:
        print 'WRITE error:%s'%e
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