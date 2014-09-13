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
        _yesterday = _now+datetime.timedelta(days=-1)
        file_path = '/data/stat/xianems/xianems_%s.txt'%_now.strftime('%Y%m%d')
        if os.path.exists(file_path):
            os.unlink(file_path)

        _date = _yesterday.strftime('%Y-%m-%d %H:%M:%S')
        _end_date = _now.strftime('%Y-%m-%d %H:%M:%S')
        sql = """SELECT `order`.`order_id`,IF(`order`.payment_type=1,'货到付款','先款后货'),`address`.ship_to,`address`.phone,`address`.tel,`order`.item_fee-`order`.discount_fee,`order_items`.item_info,`order`.express_number,`address`.province,`address`.city,`address`.district,`address`.street1,`order`.delivery_time,`order`.user_remark
                FROM `order`
                JOIN `user` ON `order`.user_id=`user`.user_id
                JOIN `address` ON `order`.shipping_address_id=`address`.id
                JOIN (SELECT `order_item`.`order_id` as oid,GROUP_CONCAT(CONCAT(`order_item`.name,'*',`order_item`.quantity) SEPARATOR '，') as item_info
                FROM `order_item` GROUP BY `order_item`.`order_id`) AS order_items ON `order`.order_id=`order_items`.oid  WHERE express_id=10 AND express_number is not null
                AND `order`.delivery_time IS NOT NULL
                AND `order`.order_type <> 14
                AND `order`.delivery_time>='%s' AND `order`.delivery_time<='%s'
        INTO OUTFILE '%s'
        FIELDS TERMINATED BY ','
        LINES TERMINATED BY '\r\n'"""%(_date,_end_date,file_path)        
        conn.execute(sql)
        print 'LUHANGYUNDA STAT COMPLETE.'
    except Exception,e:
        print 'CRON_LHYD_STAT_HANDLER happen error:%s'%e
    finally:
        conn.close()
