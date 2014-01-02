#coding=utf-8
import sys,os
sys.path.append('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]))
import datetime

from global_settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine

from collections import defaultdict

if __name__ == '__main__':
    #create table ai7mtest.coal_0424 select * from efu_coal;
    db = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=240, echo=False)
    conn = db.connect()
    #清理每日分配订单次数
    m1 = []
    m2 = []
    m3 = []
    data = conn.execute('SELECT id,pid,level,name FROM `coal_0524`')

    _origins = []
    for id,pid,level,name in data:
        if pid==0:
            m1.append((id,pid,name))
        else:
            _origins.append((id,pid,name))

    m1_IDs = map(lambda m:m[0],m1)
    for id,pid,name in _origins:
        if pid in m1_IDs:m2.append((id,pid,name))

    m2_IDs = map(lambda m:m[0],m2)
    for id,pid,name in _origins:
        if pid in m2_IDs:m3.append((id,pid,name))

    # for id,pid,level,name in data:
    #     if level == 1:m1.append((id,pid,name))
    #     if level == 2:m2.append((id,pid,name))
    #     if level == 3:m3.append((id,pid,name))

    datas = []
    for id1,pid1,name1 in m1:
        _m2s = []
        for id2,pid2,name2 in m2:
            if pid2<>id1:continue
            _m3s = [name2]
            for id3,pid3,name3 in m3:
                if pid3<>id2:continue
                _m3s.append(name3)
            _m2s.append(','.join(_m3s))
        datas.append('%s$%s'%(name1,'|'.join(_m2s)))
    print '#'.join(datas)