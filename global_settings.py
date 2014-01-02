# -*- coding: utf-8 -*-
DEBUG = True
SECRET_KEY = '0dc2a52516784b9f8dff69c872asff5'

PROPAGATE_EXCEPTIONS = True

#数据库配置
#SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://ai7m:ai7mecp@10.10.10.231/ai7m?charset=utf8'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://ai7m:ai7mecp@10.10.10.231/ai7mtest?charset=utf8'
#SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://ecp:ecp1230@localhost/ecp?charset=utf8'
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_POOL_TIMEOUT = 10
SQLALCHEMY_POOL_RECYCLE = 3600

SQLALCHEMY_BINDS = {
    'analytics':'mysql+mysqldb://ai7m:ai7mecp@10.10.10.231/analytics?charset=utf8'
}

#缓存服务器地址
MEMCACHED_SERVER = ['127.0.0.1:11211']

#日志地址
LOG_PATH = 'D:\ecpjohn\ecpjohnlog'


#短信配置
SMS_CDKEY = '6SDK-EMY-6688-JIXLN'
SMS_PASSWORD = '901170'

SEND_SMS_URI = 'http://sdk4report.eucp.b2m.cn:8080/sdkproxy/sendsms.action'
SEND_TIME_SMS_URI = 'http://sdk4report.eucp.b2m.cn:8080/sdkproxy/sendtimesms.action'