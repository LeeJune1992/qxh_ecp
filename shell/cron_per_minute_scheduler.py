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
        conn.execute('UPDATE `user` SET `assign_operator_id`=NULL,`assign_time`=now(),`assign_retain_time`=0,`intent_level_flag`=1 WHERE `assign_operator_id` IS NOT NULL AND `order_num`=0 AND `assign_retain_time`>0 AND `assign_time`<(now()-INTERVAL `assign_retain_time` HOUR)')

        #地面已购改为会员客户
        conn.execute('UPDATE `user` SET `user_type`=2 WHERE `assign_operator_id` IS NOT NULL AND `order_num`=0 AND `assign_retain_time`>0 AND `assign_time`<(now()-INTERVAL `assign_retain_time` HOUR) AND `origin`=13')
        #空盒换大礼创建1小时流转到服务公共库
        conn.execute('INSERT INTO `user_assign_log`(`user_id`,`user_type`,`assign_time`,`is_abandon`) SELECT `user_id`,5,NOW(),0 FROM `user` WHERE DATE_ADD(join_time,INTERVAL 1 HOUR)<now() AND `origin`=19 AND user_type=1')
        conn.execute('UPDATE user SET user_type=5,`assign_operator_id`=NULL,`assign_time`=now(),`assign_retain_time`=0,`intent_level_flag`=1 where DATE_ADD(join_time,INTERVAL 1 HOUR)<now() AND `origin`=19 AND user_type=1')
        #刮刮卡2015创建1小时流转到服务公共库
        conn.execute('INSERT INTO `user_assign_log`(`user_id`,`user_type`,`assign_time`,`is_abandon`) SELECT `user_id`,5,NOW(),0 FROM `user` WHERE DATE_ADD(join_time,INTERVAL 1 HOUR)<now() AND `origin`=27 AND user_type=1')
        conn.execute('UPDATE user SET user_type=5,`assign_operator_id`=NULL,`assign_time`=now(),`assign_retain_time`=0,`intent_level_flag`=1 where DATE_ADD(join_time,INTERVAL 1 HOUR)<now() AND `origin`=27 AND user_type=1')
        #服务客户 60 天后 流转到  服务流转 公共库
        #conn.execute('INSERT INTO `user_servicelz`(`user_id`,`intent_level`,`assign_time`,`time`) SELECT `user_id`,`intent_level`,`assign_time`,NOW() FROM `user` WHERE `assign_operator_id` IS NOT NULL AND DATE_ADD(assign_time,INTERVAL 1440 HOUR)<now() AND user_type=5')
        #conn.execute('INSERT INTO `user_assign_log`(`user_id`,`user_type`,`assign_time`,`is_abandon`) SELECT `user_id`,6,NOW(),0 FROM `user` WHERE `assign_operator_id` IS NOT NULL AND DATE_ADD(assign_time,INTERVAL 1440 HOUR)<now() AND user_type=5')
        #conn.execute('UPDATE user SET user_type=6,`assign_operator_id`=NULL,`assign_time`=now(),`assign_retain_time`=0 where `assign_operator_id` IS NOT NULL AND DATE_ADD(assign_time,INTERVAL 1440 HOUR)<now() AND user_type=5')
        
        
        #conn.execute('INSERT INTO `user_servicelz`(`user_id`,`intent_level`,`assign_time`,`time`) SELECT `user_id`,`intent_level`,`assign_time`,NOW() FROM `user` WHERE `assign_operator_id` IS NOT NULL AND DATE_ADD(assign_time,INTERVAL 1 MINUTE)<now() AND user_type=5')
        #conn.execute('INSERT INTO `user_assign_log`(`user_id`,`user_type`,`assign_time`,`is_abandon`) SELECT `user_id`,6,NOW(),0 FROM `user` WHERE `assign_operator_id` IS NOT NULL AND DATE_ADD(assign_time,INTERVAL 1 MINUTE)<now() AND user_type=5')
        #conn.execute('UPDATE user SET user_type=6,`assign_operator_id`=NULL,`assign_time`=now(),`assign_retain_time`=0 where `assign_operator_id` IS NOT NULL AND DATE_ADD(assign_time,INTERVAL 1 MINUTE)<now() AND user_type=5')

        
        
        
        #conn.execute('UPDATE `user` SET assign_operator_id=operator_id,assign_time=join_time,assign_retain_time=0 WHERE `user`.operator_id IN (56,67)')
        #分销商可以流转
        trans.commit()
    except Exception,e:
        trans.rollback()
        print 'CRON_LOOP_TIMER happen error:%s'%e
    finally:
        conn.close()
