#coding=utf-8
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
import datetime

from global_settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from collections import defaultdict
from settings.constants import STORES
from utils.tools import printException

if __name__ == '__main__':
    print '[CRON]%s -> %s'%(__file__,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=240, echo=False)
    conn = db.connect()
    trans = conn.begin()
    try:
        #清理每日分配订单次数
        conn.execute('UPDATE `operator` SET `assign_orders`=0')

        #每日商品库存量备份
        _now = datetime.datetime.now()
        _yesterday = _now+datetime.timedelta(days=-1)
        conn.execute('CREATE TABLE `stock_%s` SELECT `sku_id`,`store_id`,`quantity` FROM `sku_stock`'%(_yesterday.strftime('%y%m%d')))

        #每日商品盘点
        _day = _yesterday.strftime('%Y-%m-%d')
        conn.execute('INSERT INTO `stock_inventory`(sku_id,store_id,`quantity`,`ins`,in_quantity,`outs`,out_quantity,`date`) SELECT `sku_id`,`store_id`,`quantity`,"",0,"",0,"%s" FROM `sku_stock`'%_day)
        #trans.commit()

        _sqls = []
        for store_id in STORES.keys():
            _items = {}
            rows = conn.execute('SELECT sku_id,c,SUM(quantity) FROM `stock_in` WHERE `status`=9 AND `valid_time`>="%s 00:00:00" AND `valid_time`<="%s" AND `store_id`=%s GROUP BY `c`,`sku_id`'%(_day,_now.strftime('%Y-%m-%d %H:%M:%S'),store_id))
            for sku_id,c,qty in rows:
                if not _items.has_key(sku_id):
                    _item = {'IN':defaultdict(int),'OUT':defaultdict(int)}
                    _items[sku_id] = _item
                else:
                    _item = _items[sku_id]
                _item['IN'][c] = qty

            rows = conn.execute('SELECT sku_id,c,SUM(quantity) FROM `stock_out` WHERE `status`=9 AND `valid_time`>="%s 00:00:00" AND `valid_time`<="%s" AND `store_id`=%s GROUP BY `c`,`sku_id`'%(_day,_now.strftime('%Y-%m-%d %H:%M:%S'),store_id))
            for sku_id,c,qty in rows:
                if not _items.has_key(sku_id):
                    _item = {'IN':defaultdict(int),'OUT':defaultdict(int)}
                    _items[sku_id] = _item
                else:
                    _item = _items[sku_id]
                _item['OUT'][c] = int(qty)

            for sku_id,d in _items.iteritems():
                ins = ','.join(['%d:%d'%(k,v) for k,v in d['IN'].iteritems()])
                in_quantity = sum(d['IN'].values())
                outs = ','.join(['%d:%d'%(k,v) for k,v in d['OUT'].iteritems()])
                out_quantity = sum(d['OUT'].values())
                _sql = 'UPDATE `stock_inventory` SET `ins`="%s",in_quantity=%d,`outs`="%s",out_quantity=%d WHERE sku_id=%d AND store_id=%d AND `date`="%s"'%(ins,in_quantity,outs,out_quantity,sku_id,store_id,_day)
                _sqls.append(_sql)

        for sql in _sqls:
            conn.execute(sql)
        trans.commit()
    except Exception,e:
        printException()
        trans.rollback()
        print 'CRON_CLEANUP happen error:%s'%e
    finally:
        conn.close()