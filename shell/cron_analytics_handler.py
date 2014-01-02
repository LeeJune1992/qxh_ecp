#coding=utf-8
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
import datetime

import urllib
from global_settings import SQLALCHEMY_BINDS
from sqlalchemy import create_engine,text
from utils.tools import printException

if __name__ == '__main__':
    print '[CRON]%s -> %s'%(__file__,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db = create_engine(SQLALCHEMY_BINDS['analytics'], pool_recycle=240, echo=False)
    conn = db.connect()
    trans = conn.begin()
    try:
        _now = datetime.datetime.now()
        _yesterday = _now+datetime.timedelta(days=-1)
        table_name = 'log_%s'%_yesterday.strftime('%Y%m%d')
        log_file_path = '/data/stat/analytics/stat-%s.log'%_yesterday.strftime('%Y%m%d')

        if not os.path.exists(log_file_path):
            raise Exception('log file(%s) is not exist.'%log_file_path)

        #DROP TABLE IF EXISTS.
        if conn.execute('SELECT COUNT(1) FROM `information_schema`.`TABLES` WHERE TABLE_NAME="%s"'%table_name).rowcount>0:
            conn.execute('DROP TABLE IF EXISTS `%s`'%table_name)
            conn.execute('COMMIT')

        conn.execute('''
        CREATE TABLE `%s` (
              `id` bigint(20) NOT NULL AUTO_INCREMENT,
              `code` varchar(50) NOT NULL,
              `msec` TIMESTAMP NOT NULL,
              `ip` varchar(50) DEFAULT NULL,
              `domain` varchar(50) DEFAULT NULL,
              `url` varchar(500) DEFAULT NULL,
              `title` varchar(500) DEFAULT NULL,
              `referrer` varchar(500) DEFAULT NULL,
              `client_id` varchar(100) DEFAULT NULL,
              `account` varchar(50) DEFAULT NULL,
              `page_id` varchar(50) NOT NULL,
              `action` varchar(50) DEFAULT NULL,
              `action_id` varchar(50) DEFAULT NULL,
              `action_name` varchar(200) DEFAULT NULL,
              PRIMARY KEY (`id`),
              KEY `ix_%s_code` (`code`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        '''%(table_name,table_name))

        _nums = 0
        f = open(log_file_path)
        _sql_template = '''INSERT INTO `%(table_name)s`
        (`code`,`msec`,`ip`,`domain`,`url`,`title`,`referrer`,`client_id`,`account`,`page_id`,`action`,`action_id`,`action_name`)
        VALUES ("%(code)s",FROM_UNIXTIME(%(msec)s),"%(ip)s","%(domain)s","%(url)s","%(title)s","%(referrer)s","%(client_id)s","%(account)s","%(page_id)s","%(action)s","%(action_id)s","%(action_name)s")'''
        for line in f.readlines():
            line = line.replace('\n','')
            code,msec,ip,domain,url,title,referrer,client_id,account,page_id,action,action_id,action_name = line.split('')[:13]
            if code:
                try:
                    _title = urllib.unquote(title.replace('\\x','%'))
                    _action_name = urllib.unquote(action_name.replace('\\x','%')) if action_name else ''
                    _referrer = urllib.unquote(referrer)
                    _sql = _sql_template%{'table_name':table_name,'code':code,'msec':msec,'ip':ip,'domain':domain,'url':url,'title':_title,'referrer':_referrer,'client_id':client_id,'account':account,'page_id':page_id,'action':action,'action_id':action_id,'action_name':_action_name}
                    conn.execute(_sql)
                    _nums += 1
                except Exception,e:
                    print printException()
        f.close()
        db.execute('INSERT INTO `ad_import_log`(`date`,`nums`,`import_time`) VALUES ("%s",%d,NOW())'%(_yesterday.strftime('%Y%m%d'),_nums))
        trans.commit()
        trans = conn.begin()
        sql = 'INSERT INTO `ad_report`(`dt`,`code`,`action`,`action_id`,`action_name`,`pv`,`ip`,`uv`) SELECT DATE_FORMAT(`msec`, "%%Y-%%m-%%d %%H:00:00") AS dt,code,action,action_id,action_name,count(1),count(distinct ip),count(distinct client_id) from `%s` group by dt,code,action,action_id,action_name'%table_name
        db.execute(text(sql))
        trans.commit()
        print 'IMPORT-AD-LOGS|%s|%s'%(_yesterday.strftime('%Y%m%d'),_nums)
    except Exception,e:
        printException()
        trans.rollback()
        print 'ANALYTICS AD error:%s'%e
    finally:
        conn.close()