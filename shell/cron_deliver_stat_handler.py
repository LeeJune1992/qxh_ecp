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
    try:
        _now = datetime.datetime.now()
        _yesterday = _now-datetime.timedelta(days=1)
        file_path = '/data/stat/stat/deliver_%s.txt'%_yesterday.strftime('%Y%m%d')
        if os.path.exists(file_path):
            os.unlink(file_path)

        _date = _yesterday.strftime('%Y-%m-%d')
        sql = """SELECT `order_id`,`order`.username,`user`.phone,`order`.item_fee-`order`.discount_fee,`order_items`.item_info,`order`.express_id,`order`.express_number,`address`.province,`address`.city,`address`.district,`address`.street1,`operator`.nickname,`order`.created
FROM `order`
JOIN `operator` ON `operator`.id = `order`.created_by
JOIN `user` ON `order`.user_id=`user`.user_id
JOIN `address` ON `order`.shipping_address_id=`address`.id
JOIN (SELECT `order_item`.`order_id` as oid,GROUP_CONCAT(CONCAT(`order_item`.name,'*',`order_item`.quantity) SEPARATOR '，') as item_info FROM `order_item` GROUP BY `order_item`.`order_id`) AS order_items ON `order`.order_id=`order_items`.oid
WHERE `order`.status IN (6,60,100) AND `order`.`order_id` IN (SELECT `order_id` FROM `order_log` WHERE `order_log`.to_status=6 AND `order_log`.operate_time>='%s 00:00:00' AND `order_log`.operate_time<='%s 23:59:59') ORDER BY `order`.created
INTO OUTFILE '%s'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'"""%(_date,_date,file_path)
        conn.execute(sql)
        print 'DELIVER STAT COMPLETE.'
    except Exception,e:
        print 'CRON_DELIVER_STAT_HANDLER happen error:%s'%e
    finally:
        conn.close()