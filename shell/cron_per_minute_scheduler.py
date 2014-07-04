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
        #处理到期新客户 - > 公共库
        conn.execute('INSERT INTO `user_assign_log`(`user_id`,`user_type`,`assign_time`,`is_abandon`) SELECT `user_id`,`user_type`,NOW(),0 FROM `user` WHERE `assign_operator_id` IS NOT NULL AND `order_num`=0 AND `assign_retain_time`>0 AND `assign_time`<(now()-INTERVAL `assign_retain_time` HOUR)')
        #地面已购改为会员客户
        conn.execute('UPDATE `user` SET `user_type`=2 WHERE `assign_operator_id` IS NOT NULL AND `order_num`=0 AND `assign_retain_time`>0 AND `assign_time`<(now()-INTERVAL `assign_retain_time` HOUR) AND `origin`=13')
        conn.execute('UPDATE `user` SET `assign_operator_id`=NULL,`assign_time`=now(),`assign_retain_time`=0 WHERE `assign_operator_id` IS NOT NULL AND `order_num`=0 AND `assign_retain_time`>0 AND `assign_time`<(now()-INTERVAL `assign_retain_time` HOUR)')
        #conn.execute('UPDATE `user` SET assign_operator_id=operator_id,assign_time=join_time,assign_retain_time=0 WHERE `user`.operator_id IN (56,67)')
        #分销商可以流转
        trans.commit()
    except Exception,e:
        trans.rollback()
        print 'CRON_LOOP_TIMER happen error:%s'%e
    finally:
        conn.close()