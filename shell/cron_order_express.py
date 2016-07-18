#coding=utf-8
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))

import  datetime

from global_settings import SQLALCHEMY_DATABASE_URI
from collections import defaultdict,deque
from sqlalchemy import create_engine

if __name__ == '__main__':
    print '[CRON]%s -> %s'%(__file__,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=240, echo=False)
    conn = db.connect()
    trans = conn.begin()
    try:
        #获取订单
        orders = conn.execute('select order_id, from `order` where status=5')
        
        #trans.commit()
        print 'ASSIGN ORDERS HANDLE COMPLETE.'
    except Exception,e:
        trans.rollback()
        print 'CRON_ORDER_ASSIGN_SCHEDULE happen error:%s'%e
    finally:
        conn.close()
