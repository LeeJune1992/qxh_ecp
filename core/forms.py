# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Markup,current_app
from flask.ext.wtf import Form,ValidationError
from flask.ext.wtf import TextAreaField,RadioField,BooleanField,IntegerField,DateField,FloatField,CheckboxInput,QuerySelectField,QuerySelectMultipleField,SelectField,SelectMultipleField,HiddenField,PasswordField,TextField,SubmitField,BooleanField,RadioField
from flask.ext.wtf import Required,Length,AnyOf,Email,Optional,EqualTo
from .models import Knowledge_Category,Operator,Item,Sku,User, Role#,Permission,
from settings.constants import  *
from flask.ext.login import current_user

from extensions import db

class KnowledgeForm(Form):
    title = TextField(u'标题',[Required(u'输入标题')])
    #category_id = QuerySelectField(u'类型',query_factory=lambda :Knowledge_Category.query.all(),get_label='name')
    content = TextAreaField('内容')


class CategoryForm(Form):
    name = TextField(u'类别名称', [Required(u'类别名称不可为空')])
    def validate_name(self, field):
        if Knowledge_Category.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(u'类别已存在')


class NewsForm(Form):
    title = TextField(u'标题', [Required(u'标题不可为空')])
    content = TextAreaField('内容')
    

class LoginForm(Form):
    next = HiddenField()
    username = TextField(u'帐号', [Required(u'帐号为空')])
    password = PasswordField('密码', [Required(u'密码为空')])


class PasswordForm(Form):
    next = HiddenField()
    password = PasswordField('旧密码', [Required()])
    new_password = PasswordField('新密码', [Required(), Length(min=6,message=u'密码不少于6个字符')])
    password_again = PasswordField('再输入一次', [Required(), Length(min=6,message=u'密码不少于6个字符'), EqualTo('new_password',message="密码输入不一致")])


    def validate_password(form, field):
        user = Operator.query.filter_by(username=current_user.username).first()
        if not user.check_password(field.data):
            raise ValidationError("密码输入错误.")


# class RoleForm(Form):
#     name = TextField(u'角色名',[Required(u'请输入角色名')])
#     permissions = QuerySelectMultipleField(u'权限列表',query_factory=lambda :Permission.query.all(),allow_blank=False,get_label='endpoint')

#    def validate_name(self, field):
#        if not self.obj and Role.query.filter_by(name=field.data).first() is not None:
#            raise ValidationError(u'角色名已存在')


def __TEAM_CHOICES():
    _choices = [('',u'无')]
    for dk,dv in DEPARTMENTS.iteritems():
        _choices.append((dk,dv))
        for tk,tv in TEAMS.iteritems():
            if tk.startswith(dk):
                _choices.append((tk,'%s > %s'%(dv,tv)))
    return _choices

TEAM_CHOICES = __TEAM_CHOICES()

class OperatorForm(Form):
    next = HiddenField()
    id = HiddenField(default=0)
    username = TextField(u'帐号', [Required(u'请输入帐号')])
    password = PasswordField(u'密码')
    nickname = TextField(u'姓名', [Required(u'请输入姓名')])
    op_id = TextField(u'工号')
    email = TextField(u'邮箱地址',[Email(u'邮箱格式不正确')])
    team = SelectField(u"所属组", [AnyOf([str(val) for val in TEAMS.keys()+DEPARTMENTS.keys()])],choices=TEAM_CHOICES)
    role = QuerySelectField(u'角色',query_factory=lambda :Role.query.all(),get_label='name')
    is_admin = BooleanField(u'设为系统管理员')
    assign_user_type = SelectField(u"指派客户类型", [AnyOf([str(val) for val in OPEARTOR_ASSIGN_USER_TYPES.keys()])],choices=[(str(val), label) for val, label in OPEARTOR_ASSIGN_USER_TYPES.iteritems()])
    store_id = SelectField(u"仓库", [AnyOf([str(val) for val in STORES2.keys()])],choices=[(str(val), label) for val, label in STORES2.items()])
    #SelectField(u"角色", [AnyOf([str(val) for val in USER_ROLE.keys()])],choices=[(str(val), label) for val, label in USER_ROLE.items()])


    #SelectField(u"角色", [AnyOf([str(val) for val in USER_ROLE.keys()])],
    #    choices=[(str(val), label) for val, label in USER_ROLE.items()])

    #is_admin = BooleanField(u'是否设为管理员')

    def validate_password(self,field):
        operator_id = int(self.id.data)
        if not operator_id:
            if not field.data or len(field.data)<6:
                raise ValidationError(u'密码为空或小于6位')
        else:
            if field.data and len(field.data)<6:
                raise ValidationError(u'密码必须不小于6位')

    def validate_username(self, field):
        operator_id = int(self.id.data)
        if not operator_id:
            if Operator.query.filter_by(username=field.data).first() is not None:
                raise ValidationError(u'用户名已存在')


# name = Column(db.String(50), nullable=False)
# gender = Column(db.SmallInteger,nullable=False,default=0)#性别
# phone = Column(db.String(15), nullable=False, unique=True)
# total_fee = Column(db.Integer, nullable=False, default=0)#累计积分
# used_fee = Column(db.Integer, nullable=False, default=0)#已用积分
# grade = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#用户等级
# origin = Column(db.SmallInteger(unsigned=True),nullable=False, default=1)#来源
# email = Column(db.String(50))#邮箱地址
# #addresses = db.relationship('address', backref=db.backref('user', lazy='joined'), lazy='dynamic')#地址列表
# remark = Column(db.String(500))#用户备注
# operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#隶属操作人员
# operator = db.relationship('Operator',backref=db.backref('users', lazy='dynamic'))
# status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:正常,2:冻结)

class UserForm(Form):
    user_id = HiddenField(default=0)
    name = TextField(u'姓名', [Required(u'请输入姓名')])
    gender = SelectField(u"性别", [AnyOf([u'保密',u'男',u'女'])],choices=[(label, label) for label in (u'保密',u'男',u'女')])
    phone = TextField(u'手机号码',[Required(u'请输入电话号码')])
    email = TextField(u'邮箱地址',[Email(u'邮箱格式不正确')])
    origin = SelectField(u"客户来源", [AnyOf([str(val) for val in USER_ORIGINS.keys()])],choices=[(str(val), label) for val, label in USER_ORIGINS.items()])
    status = SelectField(u"状态", [AnyOf([str(val) for val in USER_STATUS.keys()])],choices=[(str(val), label) for val, label in USER_STATUS.items()])

    def validate_phone(self, field):
        _user_id = int(self.user_id.data)
        if not _user_id:
            if User.query.filter(User.phone==field.data).first() is not None:
                raise ValidationError(u'电话号码已存在')
        else:
            if User.query.filter(db.and_(User.phone==field.data,User.user_id!=_user_id)).first() is not None:
                raise ValidationError(u'电话号码已存在')


class ItemForm(Form):
    name = TextField(u'商品名称',[Required(u'输入商品名称')])
    category_id = SelectField(u"类型", [AnyOf([str(val) for val in ITEM_CATEGORYS.keys()])],choices=[(str(val), label) for val, label in ITEM_CATEGORYS.items()])
    desc = TextField(u'描述')

    def validate_name(self, field):
        if Item.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(u'商品已存在')


def validate_gte_0(form,field):
    if field.data<0:
        raise ValidationError(u'%s必须大于等于0'%field.label.text)

class SkuForm(Form):
    name = TextField(u'SKU名称',[Required(u'输入SKU名称')])
    item = QuerySelectField(u'商品',query_factory=lambda :Item.query.filter(Item.status==True), get_label='name')
    p1 = TextField(SKU_PROPERTIES_NAME['p1'])
    p2 = TextField(SKU_PROPERTIES_NAME['p2'])
    p3 = TextField(SKU_PROPERTIES_NAME['p3'])
    code = TextField(u'商品条码',[Required(u'商品条码不允许为空')])
    # price = FloatField(u'零售价',[validate_gte_0])
    # market_price = FloatField(u'市场价',[validate_gte_0])
    # discount_price = FloatField(u'活动价',[validate_gte_0],default=0)
    price = FloatField(u'零售价')
    market_price = FloatField(u'市场价')
    discount_price = FloatField(u'活动价')
    allowed_gift = BooleanField(u'是否允许为赠品')
    unit = SelectField(u"单位", [AnyOf(SKU_UNITS)],choices=[(u, u) for u in SKU_UNITS])
    threshold = IntegerField(u'阀值',[validate_gte_0],default=200)
    warning_threshold = IntegerField(u'警戒值',[validate_gte_0],default=500)
    status = BooleanField(u'是否启用',default=True)

def skus():
    return Sku.query.filter(Sku.status==True)


class StockInForm(Form):
    sku = QuerySelectField(u'商品',query_factory=skus,get_label='name')
    store_id = SelectField(u"仓库", [AnyOf([str(val) for val in STORES.keys()])],choices=[(str(val), label) for val, label in STORES.items()])
    c = SelectField(u"入库方式", [AnyOf([str(val) for val in STOCK_IN_CATEGORIES_IDs])],choices=[(str(val), STOCK_IN_CATEGORIES[val]) for val in STOCK_IN_CATEGORIES_IDs])
    shelf_number = TextField(u'货架号')
    code = TextField(u'入库凭证')
    made_in = TextField(u'产地')
    purchase_price = FloatField(u'进货价',default=0.0)
    mfg_date = DateField(u'生产日期',[Optional()])
    exp_date = DateField(u'有效期至',[Optional()])
    quantity = IntegerField(u'入库数量',[validate_gte_0])
    order_id = TextField(u'关联订单号')
    remark = TextAreaField(u'备注')


class StockOutForm(Form):
    sku = QuerySelectField(u'商品',query_factory=skus,get_label='name')
    store_id = SelectField(u"仓库", [AnyOf([str(val) for val in STORES.keys()])],choices=[(str(val), label) for val, label in STORES.items()])
    c = SelectField(u"出库类型", [AnyOf([str(val) for val in STOCK_OUT_CATEGORIES_IDs])],choices=[(str(val), STOCK_OUT_CATEGORIES[val]) for val in STOCK_OUT_CATEGORIES_IDs])
    code = TextField(u'出库凭证')
    purchase_price = FloatField(u'进货价',default=0.0)
    quantity = IntegerField(u'出库数量',[validate_gte_0])
    order_id = TextField(u'关联订单号')
    remark = TextAreaField(u'备注')

#
# sku_id = Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)
# quantity = Column(db.Integer(unsigned=True), default=0)#报损数量
# type = Column(db.SmallInteger, nullable=False, default=1)#报损类型（1:订单、2:人工报损）
# link_order_id = Column(db.BigInteger, db.ForeignKey('order.order_id'),nullable=True)#关联订单ID
# remark = Column(db.String(500))#报损备注
# status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:未审批,2:待审批,9:已报损)
# created = Column(db.DateTime, default=datetime.now)
# operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#隶属操作人员
# operator = db.relationship('Operator', backref=db.backref('losses', lazy='dynamic'))

class LossForm(Form):
    sku = QuerySelectField(u'商品',query_factory=lambda:Sku.query.all(),get_label='name')
    quantity = IntegerField(u'报损数量',[validate_gte_0])
    channel = SelectField(u"损坏渠道", [AnyOf([str(val) for val in LOSS_CHANNELS.keys()])],choices=[(str(val), label) for val, label in LOSS_CHANNELS.items()])
    degree = SelectField(u"损坏情况", [AnyOf([str(val) for val in LOSS_DEGREES.keys()])],choices=[(str(val), label) for val, label in LOSS_DEGREES.items()])
    link_order_id = TextField(u'关联订单号')
    remark = TextAreaField(u'原因备注')



# class OrderForm(Form):
#     user_id = HiddenField()
#     username = TextField(u'客户姓名')
#     order_type = SelectField(u"订单类型", [AnyOf([str(val) for val in ORDER_TYPES.keys()])],choices=[(str(val), label) for val, label in ORDER_TYPES.items()])
#     order_mode = SelectField(u"成交方式", [AnyOf([str(val) for val in ORDER_MODES.keys()])],choices=[(str(val), label) for val, label in ORDER_MODES.items()])
#     payment_type = RadioField(u"付款方式", [AnyOf([str(val) for val in ORDER_PAYMENTS.keys()])],choices=[(str(val), label) for val, label in ORDER_PAYMENTS.items()],default=1)
#     item = QuerySelectField(u'选择产品',query_factory=Sku.allowed_order_skus,get_label=lambda o:o.name)
#     quantity = IntegerField(u'数量')
#     remark = TextAreaField(u'备注')






