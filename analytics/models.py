#coding=utf-8
from datetime import datetime,timedelta
from sqlalchemy import UniqueConstraint, event, DDL, Column, Table, asc, desc, func
from sqlalchemy.orm import relationship, backref, deferred
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from extensions import db

from constants import *

from hashlib import md5


class AD_Product(db.Model):
    '''产品列表'''

    __bind_key__ = 'analytics'
    __tablename__ = 'ad_product'

    id = Column(db.Integer(unsigned=True), primary_key=True)
    name = Column(db.String(50),nullable=False)
    type = Column(db.SmallInteger(unsigned=True),nullable=False,index=True)#(1:药品、2:商品)
    remark = Column(db.String(500))

    @property
    def type_name(self):
        return AD_PRODUCT_TYPES[self.type]


event.listen(AD_Product.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=10;'))


class AD_Medium(db.Model):
    '''媒体'''

    __bind_key__ = 'analytics'
    __tablename__ = 'ad_medium'

    id = Column(db.Integer(unsigned=True), primary_key=True)
    name = Column(db.String(50),nullable=False)
    url = Column(db.String(50))

event.listen(AD_Medium.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=100;'))


class AD_Place(db.Model):
    '''广告位'''

    __bind_key__ = 'analytics'
    __tablename__ = 'ad_place'

    id = Column(db.Integer(unsigned=True), primary_key=True)
    medium_id = Column(db.Integer, db.ForeignKey('ad_medium.id'), nullable=False)
    name = Column(db.String(50),nullable=False)
    url =  Column(db.String(100))
    remark = Column(db.String(500))
    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:正常)
    created = Column(db.DateTime, default=datetime.now)

    medium = db.relationship('AD_Medium', backref=db.backref('places', lazy='dynamic'))

    @hybrid_property
    def fullname(self):
        return u'%s -> %s'%(self.medium.name,self.name)

event.listen(AD_Place.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=1000;'))


class AD_Content(db.Model):
    '''广告内容'''

    __bind_key__ = 'analytics'
    __tablename__ = 'ad_content'

    id = Column(db.Integer(unsigned=True), primary_key=True)
    name = Column(db.String(50),nullable=False)
    mode = Column(db.SmallInteger(unsigned=True),nullable=False,index=True)#方式(1:文字、2:图片)
    type = Column(db.SmallInteger(unsigned=True),nullable=False,index=True)#类型(1:专题、2:链接)
    img = Column(db.String(200))#图片
    txt = Column(db.String(100))#文字
    to_url = Column(db.String(200),nullable=False)#投放地址
    remark = Column(db.String(500))#备注

    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:正常)
    created = Column(db.DateTime, default=datetime.now)

    @hybrid_property
    def fullname(self):
        return u'%s.%s -> %s'%(self.mode_name,self.name,self.type_name)

    @property
    def mode_name(self):
        return AD_CONTENT_MODES[self.mode]

    @property
    def type_name(self):
        return AD_CONTENT_TYPES[self.type]

event.listen(AD_Content.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=10000;'))


from urlparse import parse_qs, urlsplit, urlunsplit
from urllib import urlencode,quote

AD_UNION_URL = 'analytics.ai7mei.com/go'

class AD(db.Model):
    '''广告'''

    __bind_key__ = 'analytics'
    __tablename__ = 'ad'

    id = Column(db.Integer(unsigned=True), primary_key=True)
    code = Column(db.String(50),nullable=False,unique=True,index=True)
    name = Column(db.String(50),nullable=False)

    product_id = Column(db.Integer(unsigned=True),index=True,nullable=False)
    product_name = Column(db.String(50),nullable=False,index=True)

    medium_id = Column(db.Integer(unsigned=True),nullable=False)
    medium_name = Column(db.String(50),nullable=False)

    place_id = Column(db.Integer(unsigned=True),nullable=False,index=True)
    place_name = Column(db.String(50),nullable=False)

    ad_id = Column(db.Integer(unsigned=True),nullable=False,index=True)
    ad_name = Column(db.String(50),nullable=False)
    ad_mode = Column(db.SmallInteger(unsigned=True),nullable=False,index=True)#方式(1:文字、2:图片)
    ad_type = Column(db.SmallInteger(unsigned=True),nullable=False,index=True)#类型(1:专题、2:链接)
    ad_img = Column(db.String(200))#图片
    ad_txt = Column(db.String(100))#文字
    ad_url = Column(db.String(200))#广告地址
    to_url = Column(db.String(200),nullable=False)#目标地址

    remark = Column(db.String(500))#备注

    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:启用)
    created = Column(db.DateTime, default=datetime.now)


    @classmethod
    def generate_code(cls,product_id,medium_id,place_id,ad_id):
        return md5('%s$%s$%s$%s'%(product_id,medium_id,place_id,ad_id)).hexdigest()

    @property
    def mode_name(self):
        return AD_CONTENT_MODES[self.ad_mode]

    @property
    def type_name(self):
        return AD_CONTENT_TYPES[self.ad_type]

    @property
    def link_url(self):
        if self.ad_type == 1:
            scheme, netloc, path, query_string, fragment = urlsplit(self.to_url)
            query_params = parse_qs(query_string)
            query_params['code'] = [self.code]
            new_query_string = urlencode(query_params, doseq=True)
            return urlunsplit((scheme, netloc, path, new_query_string, fragment))
        elif self.ad_type==2:
            return urlunsplit(('http', AD_UNION_URL, '', urlencode({'code':self.code,'to':quote(self.to_url)},doseq=True), ''))


event.listen(AD_Content.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=100000;'))


class AD_Import_Log(db.Model):
    __tablename__ = 'ad_import_log'
    __bind_key__ = 'analytics'

    id = Column(db.Integer(unsigned=True), primary_key=True)
    date = Column(db.String(50),nullable=False)
    nums = Column(db.Integer,nullable=False,default=0)
    import_time = Column(db.DateTime, default=datetime.now)#导入时间


class AD_Report(db.Model):

    __tablename__ = 'ad_report'
    __bind_key__ = 'analytics'

    id = Column(db.Integer(unsigned=True), primary_key=True)
    dt = Column(db.DateTime, nullable=False)
    code = Column(db.String(50),index=True)
    action = Column(db.String(50))
    action_id = Column(db.String(50),index=True)
    action_name = Column(db.String(50))
    pv = Column(db.Integer,nullable=False,default=0)
    ip = Column(db.Integer,nullable=False,default=0)
    uv = Column(db.Integer,nullable=False,default=0)

