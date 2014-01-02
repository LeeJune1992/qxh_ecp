#coding=utf-8
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
import datetime

from global_settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine

if __name__ == '__main__':
    db = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=240, echo=False)
    conn = db.connect()
    trans = conn.begin()
    try:
        datas = conn.execute('''
        SELECT name,phone,phone_1,address,dialog_content,op_id,create_date FROM `ai7mtest`.`xl_user` as `tmp_user`
        WHERE tmp_user.phone not in ()
        ''')
        xl_users = []
        for d in datas:
            xl_users.append(d)

        print xl_users[:10]
        trans.commit()
    except Exception,e:
        trans.rollback()
        print 'CRON_CLEANUP happen error:%s'%e
    finally:
        conn.close()