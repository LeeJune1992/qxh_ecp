# -*- coding: utf-8 -*-
import uuid
import hashlib
import sys
import traceback
from Crypto.Cipher import DES
from global_settings import SECRET_KEY


class Des:
    def __init__(self):
        self._des = DES.new('afh9Adas')

    def encrypt(self,value):
        value = value+' '*(8-len(value)%8)
        return self._des.encrypt(value).encode('hex')

    def decrypt(self,token):
        return self._des.decrypt(token.decode('hex')).strip(' ')

    def user_token(self,user_id):
        return self.encrypt(str(user_id))

    def validate_user_token(self,token,user_id):
        try:
            _value = self.decrypt(str(token))
            if _value == str(user_id):return True
            return False
        except:
            return False


des = Des()


def printException(level=6):
    '''
    打印错误信息
    @param level:错误等级
    '''
    error_type,error_value,trbk = sys.exc_info()
    print 'Type:%s'%error_type.__name__
    print 'Description:%s' % error_value
    print 'Traceback (most recent call last):'
    for err in traceback.format_tb(trbk, level):
        print err

def generate_key(length):
    return hashlib.sha512(uuid.uuid4().hex).hexdigest()[:length]

def md5(value):
    return hashlib.md5(value).hexdigest()

def converse_s_2_dhms_zh(s):
    min,s=divmod(s,60)
    h,min=divmod(min,60)
#    d,h=divmod(h,24)
    _result = ''
#    if d>0:
#        _result += u'%d天'%d
    if h>0:
        _result += u'%d小时'%h
    if min>0:
        _result += u'%d分'%min
    return _result


def delta_s(t1, t2):
    '''
    计算两个时间相差的秒数
    '''
    delta = t1 - t2
    return 86400 * delta.days + delta.seconds

class str2dict(dict):
    '''
        字符串转换成字典
        example:
            >>> d=__dic()
            >>> a='x:1,y:2.5,m:hello'
            >>> print eval('{%s}' % a,d)
                {'y': 2.5, 'x': 1, 'm': 'hello'}
    '''
    def __getitem__(self,attr):
        return ( attr )

    def get(self,k,dv=None):
        return self.__getitem__(k)

    def has_key(self,k):
        return True

    def __contains__(self,k):
        return True

c_dict = str2dict()
