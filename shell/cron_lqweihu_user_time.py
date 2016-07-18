# -*- coding:utf-8 -*-
'''
time: 2016/04/08
author: wanghaifei
'''
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))

from sqlalchemy import create_engine
from global_settings import SQLALCHEMY_DATABASE_URI
from collections import defaultdict
import datetime

if __name__ == '__main__':
    '''
    更新user_assign_time_log这个数据表
    '''
    print '[CRON]%s -> %s'%(__file__,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    db = create_engine(SQLALCHEMY_DATABASE_URI,echo=False)
    connect = db.connect()
    try:
        sql1 = '''update user_assign_log set one_two=NULL'''
        connect.execute(sql1)

        sql2 = '''select ua.id,ua.user_id,ua.user_type,ua.assign_time,u.name,u.phone from user_assign_log ua
                 JOIN `user` u ON u.user_id=ua.user_id
                 where ua.user_type=1'''
        rows2 = connect.execute(sql2)
        time_logs = defaultdict(list)
        user_logs = defaultdict(list)
        for i in rows2:
            time_logs[i[1]] = i[0]

        for m in time_logs.keys():
            sql3 = '''
                select ua.id,ua.user_id,ua.user_type,u.assign_time,u.name from user_assign_log ua
                JOIN `user` u ON u.user_id=ua.user_id
                where ua.id >%s and ua.user_id=%s and ua.user_type=2 ORDER BY ua.id asc limit %d ''' % (time_logs[m],m,1)
            rows3 = connect.execute(sql3)
            for rows in rows3:
                user_logs[rows[1]] = rows[0]

        for n in user_logs.keys():
            sql3 = '''update user_assign_log set one_two=1 where id=%s''' % user_logs[n]
            connect.execute(sql3)
    except Exception,e:
        print 'CRON_LQWEIHU_USER_TIME happen error:%s'%e
    finally:
        connect.close()

