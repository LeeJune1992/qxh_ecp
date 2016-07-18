#coding=utf-8
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
import datetime

from global_settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine

if __name__ == '__main__':
    print '[CRON]%s -> %s'%(__file__,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=240, echo=False)
    conn = db.connect()
    trans = conn.begin()
    try:
        #消费3000为会员
        conn.execute('update `user` set user_label=2,hy_time=now() where user_type=2 and user_label=1 and order_fee>=3000')
        #进入维护3个月后为会员
        sql = '''update `user` set user_label=2,hy_time=now() where user_type=2 and user_label=1 and member_time<DATE_ADD(NOW(),INTERVAL -3 MONTH)'''
        print sql
        conn.execute(sql)
        sql = '''update `user` set user_label=2,hy_time=now() where user_type=2 and user_label=1 and member_time is null and join_time<DATE_ADD(NOW(),INTERVAL -3 MONTH)'''
        conn.execute(sql)

        #6个月没有订单的为激活
        sql = '''update `user` set user_label=3 where user_type=2 and user_label=2 and hy_time<DATE_ADD(NOW(),INTERVAL -6 MONTH)'''
        conn.execute(sql)
        
        trans.commit()
    except Exception,e:
        trans.rollback()
        print 'CRON_LOOP_TIMER happen error:%s'%e
    finally:
        conn.close()
