#coding=utf-8
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Markup,current_app
from flask.ext.wtf import Form,ValidationError
from flask.ext.wtf import TextAreaField,RadioField,BooleanField,IntegerField,DateField,FloatField,CheckboxInput,QuerySelectField,QuerySelectMultipleField,SelectField,SelectMultipleField,HiddenField,PasswordField,TextField,SubmitField,BooleanField,RadioField
from flask.ext.wtf import Required,Length,AnyOf,Email,Optional,EqualTo
from constants import *

from .models import AD_Product,AD_Medium,AD_Place,AD_Content

class ProductForm(Form):
    name = TextField(u'产品名称',[Required(u'请输入产品名称')])
    type = SelectField(u"分类", [AnyOf([str(val) for val in AD_PRODUCT_TYPES.keys()])],choices=[(str(val), label) for val, label in AD_PRODUCT_TYPES.items()])
    remark = TextField(u'备注')

class MediumForm(Form):
    name = TextField(u'媒体名称',[Required(u'请输入媒体名称')])
    url = TextField(u'链接地址',default='http://')


class PlaceForm(Form):
    medium = QuerySelectField(u'媒体',query_factory=lambda :AD_Medium.query.all(), get_label='name')
    name = TextField(u'广告位名称',[Required(u'请输入广告位名称')])
    url = TextField(u'链接地址',default='http://')
    remark = TextField(u'备注')


class ContentForm(Form):
    name = TextField(u'名称',[Required(u'请输入名称')])
    type = SelectField(u"类型", [AnyOf([str(val) for val in AD_CONTENT_TYPES.keys()])],choices=[(str(val), label) for val, label in AD_CONTENT_TYPES.items()])
    mode = SelectField(u"广告展示形式", [AnyOf([str(val) for val in AD_CONTENT_MODES.keys()])],choices=[(str(val), label) for val, label in AD_CONTENT_MODES.items()])
    img = TextField(u'图片链接地址',[Optional()],default='http://')
    txt = TextField(u'关键字')
    to_url = TextField(u'目标链接地址',default='http://')
    remark = TextAreaField(u'备注',[Optional()])


class ADForm(Form):
    name = TextField(u'名称',[Required(u'请输入名称')])
    product = QuerySelectField(u'产品',query_factory=lambda :AD_Product.query.all(), get_label='name')
    place = QuerySelectField(u'媒体广告位',query_factory=lambda :AD_Place.query.order_by(AD_Place.medium_id), get_label='fullname')
    content = QuerySelectField(u'展示内容',query_factory=lambda :AD_Content.query.all(), get_label='fullname')
    remark = TextAreaField(u'备注',[Optional()])

