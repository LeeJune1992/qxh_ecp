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
        #获取待分配订单列表
        role_link_orders = defaultdict(list)
        need_assign_orders = conn.execute('SELECT order_id,assign_role_id FROM `order` WHERE `need_assign`=1')
        for order_id,assign_role_id in need_assign_orders:
            role_link_orders[assign_role_id].append(order_id)

        if len(role_link_orders)==0:
            conn.close()
            print 'NO ORDERS NEED TO BE ASSIGNED.'
            sys.exit(0)

        #获取可分配任务的操作员列表
        role_list = ','.join(map(str,role_link_orders.keys()))
        _operators = defaultdict(deque)
        allowed_assign_operators = conn.execute('SELECT `id`,`role_id`,`assign_orders`,`username` FROM `operator` WHERE `role_id` in (%s) AND `status`=1 ORDER BY `assign_orders`'%role_list)
        for op_id,role_id,assign_orders,username in allowed_assign_operators:
            _operators[role_id].append((op_id,username))

        _update_sql = []
        #分配订单操作
        operator_assign_orders = defaultdict(int)
        for role_id,order_ids in role_link_orders.iteritems():
            if not _operators.has_key(role_id):
                print 'ASSIGN_ORDERS|%d|NOBODY.'%role_id
                continue
            role_ops = _operators[role_id]
            for order_id in order_ids:
                op_id,op_name = role_ops[0]
                _update_sql.append('UPDATE `order` SET `assign_operator_id`=%d,`need_assign`=0 WHERE `order_id`="%s"'%(op_id,str(order_id)))
                print 'ORDER_ASSIGN|%s|%s|%s'%(order_id,op_id,op_name)
                operator_assign_orders[op_id]+=1
                role_ops.rotate(-1)

        #更新操作员分配订单数
        for op_id,num in operator_assign_orders.iteritems():
            _update_sql.append('UPDATE `operator` SET `assign_orders`=`assign_orders`+%d WHERE `id`=%d'%(num,op_id))

        #执行SQL
        for sql in _update_sql:
            conn.execute(sql)
        trans.commit()
        print 'ASSIGN ORDERS HANDLE COMPLETE.'
    except Exception,e:
        trans.rollback()
        print 'CRON_ORDER_ASSIGN_SCHEDULE happen error:%s'%e
    finally:
        conn.close()