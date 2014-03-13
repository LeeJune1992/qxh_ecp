#coding=utf-8
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
import datetime

from global_settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine

if __name__ == '__main__':
    print '[CRON]%s -> %s'%(__file__,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    db = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=240, echo=False)
    conn = db.connect()
    trans = conn.begin()
    try:
        #
        sql = '''SET @@GROUP_CONCAT_MAX_LEN=9999999999;INSERT INTO `user_statistics` (tjdate,new_users,giveup_users,users,hg_users,cm_users,tj_users,city_users,xian_users,hg_user_list,cm_user_list_user_list) values(
(DATE_FORMAT(now(),'%%Y-%%m-%%d')),(select count(*) from `user` where member_time=DATE_FORMAT(now(),'%%Y-%%m-%%d'))
,(select count(*) from `user_giveup` where status=1 AND DATE_FORMAT(audit_time,'%%Y-%%m-%%d')=DATE_FORMAT(now(),'%%Y-%%m-%%d'))
,(select count(distinct user_id) from `user` where batch_id IS NULL AND user_type=2)
,(select count(distinct u.user_id) from `user` u join `order` o on o.user_id=u.user_id where u.batch_id IS NULL AND u.user_type=2 and datediff(now(),o.created)<=90)
,(select count(distinct u.user_id) from `user` u where u.batch_id IS NULL AND u.user_type=2 and u.user_id not in (select user_id from `order` where datediff(now(),created)<=90))
,(select count(*) from `user` where origin=5)
,(select count(distinct a.user_id) from address a join `user` u on u.user_id=a.user_id where u.batch_id IS NULL AND u.user_type=2 and a.district like '%%县')
,(select count(distinct a.user_id) from address a join `user` u on u.user_id=a.user_id where u.batch_id IS NULL AND u.user_type=2 and (a.district IS NULL or a.district ='' or a.district like '%%区'))
,(select group_concat(distinct u.user_id) from `user` u join `order` o on o.user_id=u.user_id where u.batch_id IS NULL AND u.user_type=2 and datediff(now(),o.created)<=90 ORDER BY u.user_id)
,(select group_concat(distinct u.user_id) from `user` u join `order` o on o.user_id=u.user_id where u.batch_id IS NULL AND u.user_type=2 and u.user_id not in (select user_id from `order` where datediff(now(),created)<=90) ORDER BY u.user_id)
        )'''
        conn.execute(sql)
        trans.commit()
    except Exception,e:
        trans.rollback()
        print 'CRON_LOOP_TIMER happen error:%s'%e
    finally:
        conn.close()
