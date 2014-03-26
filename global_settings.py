# -*- coding: utf-8 -*-
DEBUG = True
SECRET_KEY = '0dc2a52516784b9f8dff69c872asff5'

PROPAGATE_EXCEPTIONS = True

#数据库配置
#SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://ai7m:ai7mecp@10.10.10.231/ai7m?charset=utf8'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://ai7m:ai7mecp@10.10.10.231/ai7mtest?charset=utf8'
#SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:root1230@localhost/ecp?charset=utf8'
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

SF_D = 'j_province=\'四川省\' j_city=\'成都市\' j_company=\'爱妻美\' j_contact=\'爱妻美\' j_tel=\'4006002000\' j_address=\'四川省成都市成华区白莲村2组103号\''
SF_Custid = '0283439931'
SF_Key = '5mS-2l:vM1[G~2;X}VZP'
SF_Url = 'http://bsp-test.sf-express.com:9090/bsp-ois/ws/expressService?wsdl'

#SF_Key = 'zNNx:G~y0OlSUpICkdiXFLf}vIYmU`BC'
#SF_Url = 'http://bsp-ois.sf-express.com/bsp-ois/ws/expressService?wsdl'

#库房
KF_ROOLEIDS = [104,1006]
KF_XIANID = 118
KF_CHENGDUID = 49