# -*- coding: utf-8 -*-
import random
from datetime import datetime,timedelta
from global_settings import *
from sqlalchemy import UniqueConstraint, event, DDL, Column, Table, asc, desc, func
from sqlalchemy.orm import relationship, backref, deferred
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from extensions import db
from utils import fields
from utils.tools import delta_s,converse_s_2_dhms_zh,des
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin,current_user
from flask import current_app,request
from settings.constants import *
from collections import defaultdict

def order_status_assign_role_id():
    _result = {}
    for role_id,status_list in ROLE_ALLOWED_ORDER_STATUS.iteritems():
        for status in status_list:
            _result[status] = role_id
    return _result

ORDER_STATUS_ASSIGN_ROLES = order_status_assign_role_id()

############################
#   订单模块
############################
class Order(db.Model):
    '''订单信息表'''
    __tablename__ = 'order'

    order_id = Column(db.BigInteger(unsigned=True), primary_key=True, autoincrement=False)
    code = Column(db.String(5),nullable=True)
    date = Column(db.Integer(unsigned=True), nullable=False, index=True)
    user_id = Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy='dynamic'))

    username = Column(db.String(50), nullable=False)
    order_type = Column(db.SmallInteger, nullable=False, default=1)#订单类型
    order_mode = Column(db.SmallInteger, nullable=False, default=1)#成交方式
    payment_type = Column(db.SmallInteger, nullable=False, default=1)#支付方式
    store_id = Column(db.SmallInteger,nullable=True)#发货库房
    item_fee = Column(db.Float(unsigned=True), nullable=False)
    shipping_fee = Column(db.Float(unsigned=True), nullable=False, default=0)
    shipping_address_id = Column(db.Integer, db.ForeignKey('address.id'))
    shipping_address = db.relationship('Address', backref=db.backref('orders', lazy='dynamic'))

    order_items = relationship('Order_Item', backref='order', lazy='dynamic')

    order_item_sets = relationship('Order_Sets', backref='order', lazy='dynamic')

    operate_log = Column(db.String(500))
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'))
    created_by = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)

    need_invoice = Column(db.Boolean, nullable=False, default=False)#是否需要发票
    invoice_name = Column(db.String(50))#发票抬头

    discount_type = Column(db.SmallInteger, nullable=False, default=1)#优惠类型
    discount_fee = Column(db.Float(unsigned=True), nullable=False, default=0)#优惠金额

    express_id = Column(db.SmallInteger, nullable=False, default=0)#快递公司
    express_number = Column(db.String(50), index=True)#快递号
    express_sfdestcode = Column(db.String(5))#顺风目的地代码
    express_sfok = Column(db.Boolean, nullable=False, default=True)#顺风确认 john
    lhyd_postal = relationship('Order_LHYD_Postal', primaryjoin="(Order_LHYD_Postal.order_id == Order.order_id)")

    remark = Column(db.String(500))#订单备注
    user_remark = Column(db.String(200))#客户备注
    team = Column(db.String(5),nullable=True,index=True)#归属组
    status = Column(db.SmallInteger, nullable=False, default=1)#订单状态
    status_flag = Column(db.SmallInteger,nullable=False,default=0)#订单状态标识(1:打印发货单、2:打印快递单...)
    created = Column(db.DateTime, default=datetime.now, index=True)
    modified = Column(db.DateTime, default=datetime.now)

    delivery_time = Column(db.DateTime,nullable=True)#发货时间
    arrival_time = Column(db.DateTime,nullable=True)#到货时间
    end_time = Column(db.DateTime,nullable=True)#完成时间

    is_picker = Column(db.Boolean,nullable=False,default=False)#是否已拣货
    need_assign = Column(db.Boolean,nullable=False,index=True)
    assign_role_id = Column(db.Integer(unsigned=True), nullable=False,default=ORDER_ROLE_ID)#分配角色ID
    assign_operator_id = Column(db.Integer, db.ForeignKey('operator.id'),nullable=True)#分配操作员ID
    link_order_id = Column(db.BigInteger, db.ForeignKey('order.order_id'),nullable=True)#关联订单ID
    client_ip = Column(db.String(20),nullable=True)#客户端IP

    publisher = db.relationship('Operator', primaryjoin="(Operator.id == Order.created_by)")
    editor = db.relationship('Operator', primaryjoin="(Operator.id == Order.operator_id)")
    assign_operator = db.relationship('Operator', primaryjoin="(Operator.id == Order.assign_operator_id)")
    is_xlj = Column(db.Boolean, nullable=False, default=True)#是否心力健 john
    voucher_id = Column(db.Integer)
    voucher_fee = Column(db.Float(unsigned=True), nullable=False)
    @property
    def store_name(self):
        if self.store_id:
            return STORES[self.store_id]
        return ''

    @property
    def user_token(self):
        return des.user_token(self.user_id)

    @property
    def is_print_express(self):
        return self.status_flag&2

    @property
    def is_print_invoice(self):
        return self.status_flag&1

    def is_authorize(self,operator):
        return True if operator.is_admin or self.assign_operator_id==operator.id else False

    def update_status(self,to_status):
        '''修改订单状态'''
        if ORDER_STATUS_ASSIGN_ROLES.has_key(to_status):#分配角色
            role_id = ORDER_STATUS_ASSIGN_ROLES[to_status]
            if role_id == ORDER_ROLE_ID:
                self.assign_operator_id = self.created_by
                self.need_assign = False
            elif to_status in [4,32,9,10,40]:#在库房这里直接分配
                if self.store_id == 1:
                    self.assign_operator_id = KF_CHENGDUID
                    self.need_assign = False
                elif self.store_id == 3:
                    self.assign_operator_id = KF_XIANID
                    self.need_assign = False
            elif to_status in [6]:#在物流内勤这里直接分配
                if self.store_id == 1:
                    self.assign_operator_id = WLNQ_CHENGDUID
                    self.need_assign = False
                elif self.store_id == 3:
                    self.assign_operator_id = WLNQ_XIANID
                    self.need_assign = False

            else:
                self.assign_operator_id = None
                self.need_assign = True
            self.assign_role_id = role_id
        else:
            self.assign_operator_id = None
            self.need_assign = False
        
        #激活数据再次订单->会员
        if self.status == 1 and to_status == 2:
            user = self.user            
            if user.user_label == 3:
                user.hy_time = datetime.now()
                user.user_label = 2

        #变更客户类型(新客户 -> 会员客户)
        if self.status == 5 and to_status in (6,100):
            user = self.user
            if user.user_type == 1:
                user.label_id = 99
                if self.actual_fee>0:#有金额的才流转到会员客户20141210 or (user.origin not in NEED_PAID_USER_ORIGINS):# and user.product_intention <> 7检测是否为付费订单扭转的来源客户 (2013.08.20)
                    user.user_type = 2
                    user.member_time = datetime.now()#成为会员客户的时间更新add john 20131120
                    _assign_op = None
                    if user.assign_retain_time==0 and user.assign_operator_id:
                        _assign_op = user.assign_operator
                    user.assign_op(_assign_op,operator_id=None,allowed_change_user_type=False)
                    user.is_assigned = False

            self.arrival_time = datetime.now()#到货时间更新
        if to_status==5:
            self.arrival_time = None

        if self.status == 4 and to_status == 5:#短信提醒
            self.delivery_time = datetime.now()
            _address = self.shipping_address
            _mobile_phones = _address.mobile_phones
            if _mobile_phones:
                _msg = u'尊敬的%s，您订购的产品已发货，由%s配送，快递单号%s，服务热线：4006002000【爱妻美】'%(_address.ship_to,EXPRESS_CONFIG[self.express_id]['name'],self.express_number)
                #暂时删除20131225SMS.add_sms(_mobile_phones,_msg,status=1,user_id=self.user_id,remark=u'发货通知',commit=False)

        if to_status>100:
            self.user.del_order(self)#删除用户订单

        if to_status>=100:self.end_time = datetime.now()
        self.status = to_status


    @classmethod
    def generate_id(cls, date):
        _date_num = db.session.query(func.count(cls.order_id)).filter(cls.date == date).scalar()
        return '%s%05d' % (date, _date_num + 1)

    @classmethod
    def generate_code(cls):
        return ''.join([str(random.choice(range(1,10))) for i in xrange(3)])

    @property
    def actual_fee(self):
        return self.item_fee - self.discount_fee

    @property
    def payment_type_name(self):
        return ORDER_PAYMENTS[self.payment_type]

    @property
    def status_name(self):
        return ORDER_STATUS[self.status]


event.listen(Order.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=1000001;'))


class Order_Sets(db.Model):
    __tablename__ = 'order_sets'

    id = Column(db.Integer, primary_key=True)
    order_id = Column(db.BigInteger(unsigned=True), db.ForeignKey('order.order_id'), nullable=False)
    sku_set_id = Column(db.ForeignKey('sku_set.id'), nullable=False)
    name = Column(db.String(50), nullable=False)#名称
    quantity = Column(db.Integer(unsigned=True), default=0)#数量
    price = Column(db.Float(unsigned=True), nullable=False)#单价


class Order_Item(db.Model):
    '''订购商品列表'''
    __tablename__ = 'order_item'
    id = Column(db.Integer, primary_key=True)
    order_id = Column(db.BigInteger(unsigned=True), db.ForeignKey('order.order_id'), nullable=False)
    sku_id = Column(db.ForeignKey('sku.id'), nullable=False)
    stock_id = Column(db.ForeignKey('stock.id'), nullable=True)
    price = Column(db.Float(unsigned=True), nullable=False)#单价
    fee = Column(db.Float(unsigned=True),nullable=False)#总计费用
    name = Column(db.String(50), nullable=False)#名称
    pkg_name = Column(db.String(50),nullable=True)#套餐名称
    quantity = Column(db.Integer(unsigned=True), default=0)#数量
    in_quantity = Column(db.Integer(unsigned=True),default=0)#入库数量
    loss_quantity = Column(db.Integer(unsigned=True),default=0)#损耗数量
    unit = Column(db.String(2),default=u'件')#单位
    code = Column(db.String(20),nullable=False)#条码
    flag = Column(db.SmallInteger(unsigned=True), nullable=False, default=0)#标识(0:未出单,1:已出单)

    sku = db.relationship('Sku', backref=db.backref('order_items', lazy='dynamic'))
    stock = db.relationship('Stock', backref=db.backref('order_items', lazy='dynamic'))

    @property
    def new_sku_id(self):
        return '%s-%d'%(self.sku_id,self.price)

    @classmethod
    def order_item_amount(cls,order_id):
        _order_items = defaultdict(int)
        objs = cls.query.filter(cls.order_id==order_id)
        for obj in objs:
            _order_items[obj.sku_id] += obj.quantity
        return _order_items

    @classmethod
    def validate_store_qty(cls,order_id,store_id):
        '''验证库存数量是否满足'''
        _item_amounts = cls.order_item_amount(order_id)
        _store_amounts = {}
        sku_stocks = Sku_Stock.query.filter(Sku_Stock.sku_id.in_(_item_amounts.keys()),
                                            Sku_Stock.store_id==store_id)
        for sku_stock in sku_stocks:
            _store_amounts[sku_stock.sku_id] = sku_stock

        is_validate = True
        for sku_id,amount in _item_amounts.iteritems():
            if not _store_amounts.has_key(sku_id):
                return False,u'所选仓库部分商品无货！'

            _sku_stock = _store_amounts[sku_id]
            if _sku_stock.actual_quantity-amount<_sku_stock.threshold:
                return False,u'所选仓库部分商品库存不足！'
        return True,None


class Order_Log(db.Model):
    __tablename__ = 'order_log'
    id = Column(db.Integer, primary_key=True)
    order_id = Column(db.BigInteger(unsigned=True), db.ForeignKey('order.order_id'), nullable=False)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)
    operate_time = Column(db.DateTime, default=datetime.now)
    to_status = Column(db.SmallInteger, nullable=False, default=0)
    remark = Column(db.String(100))#备注
    ip = Column(db.String(30))#ip
    operator = db.relationship('Operator', backref=db.backref('order_logs', lazy='dynamic'))

    @classmethod
    def log_by_order_id(cls, order_id):
        results = []
        logs = cls.query.join(Operator, Operator.id == cls.operator_id).filter(cls.order_id == order_id).order_by(
            cls.operate_time)
        for log in logs:
            results.append({'id':log.operator_id,
                            'name': log.operator.nickname,
                            'status': ORDER_STATUS[log.to_status],
                            'time': log.operate_time,
                            'ip': log.ip,
                            'remark': log.remark})
        return results


############################
#   商品模块
############################

class Item(db.Model):
    '''商品配置表'''

    __tablename__ = 'item'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(50), nullable=False, unique=True)
    category_id = Column(db.SmallInteger, nullable=False, default=0)
    desc = Column(db.String(500))
    status = Column(db.Boolean, nullable=False, default=True)

    skus = relationship('Sku', backref='item', lazy='dynamic')

    @property
    def category_name(self):
        return ITEM_CATEGORYS[self.category_id]


class Sku_Set(db.Model):
    '''套装配置表'''
    __tablename__ = 'sku_set'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(50), nullable=False)
    config = Column(fields.Dict(200), nullable=False)
    price_config = Column(fields.Dict(300),nullable=False)
    price = Column(db.Float(unsigned=True), nullable=False)#总价
    is_valid = Column(db.Boolean, nullable=False, default=True)#是否启用
    created = Column(db.DateTime, default=datetime.now)

    @classmethod
    def allowed_order_skus(cls):
        _items = []
        sku_sets = cls.query.filter(cls.is_valid == True)
        for sku_set in sku_sets:
            _items.append({'id': '%s-%d'%(sku_set.id,sku_set.price),'sku_id':sku_set.id,'type': 2, 'unit': u'套', 'name': sku_set.name, 'price': sku_set.price})
        return _items

    @property
    def skus(self):
        objs = Sku.query.filter(Sku.id.in_(self.config.keys()))
        _datas = []
        for obj in objs:
            _n = self.config.get(obj.id, 0)
            if _n > 0: _datas.append((obj, _n))
        return _datas


event.listen(Sku_Set.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=1001;'))


class Sku(db.Model):
    '''存货单元配置表'''

    __tablename__ = 'sku'

    id = Column(db.Integer, primary_key=True)
    item_id = Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    name = Column(db.String(50), nullable=False)
    properties = Column(fields.Dict(200))#商品属性
    unit = Column(db.String(2), default=u'件')
    code = Column(db.String(20), nullable=False,index=True)#条码号
    price = Column(db.Float(unsigned=True), nullable=False)#零售价
    market_price = Column(db.Float(unsigned=True), nullable=False)#市场价
    discount_price = Column(db.Float(unsigned=True), nullable=False)#优惠价
    allowed_gift = Column(db.Boolean,nullable=False,default=False)#是否允许为赠品
    quantity = Column(db.Integer(unsigned=True), default=0)#库存数量
    order_quantity = Column(db.Integer(unsigned=True), default=0)#销售数量
    loss_quantity = Column(db.Integer(unsigned=True), default=0)#报损数量
    threshold = Column(db.Integer(unsigned=True), default=0)#阀值
    warning_threshold = Column(db.Integer(unsigned=True),default=0)#警戒值
    created = Column(db.DateTime, default=datetime.now)
    modified = Column(db.DateTime, default=datetime.now)
    status = Column(db.Boolean, nullable=False, default=True)#是否启用

    @property
    def allowed_prices(self):
        if self.allowed_gift:
            return [self.actual_price,0.0]
        else:
            return [self.actual_price]

    @property
    def gift_name(self):
        return u'%s【赠品】'%self.name

    @classmethod
    def allowed_order_skus(cls):
        _items = []
        skus = cls.query.filter(cls.status == True)
        for sku in skus:
            _price = sku.actual_price
            _items.append({'id': '%s-%d'%(sku.id,_price),'sku_id':sku.id, 'type': 1, 'unit': sku.unit, 'name': sku.name, 'price': _price})
            if _price>0 and sku.allowed_gift:
                _items.append({'id': '%s-0'%sku.id,'sku_id':sku.id,'type': 1, 'unit': sku.unit, 'name': sku.gift_name, 'price': 0})
        return _items

    @property
    def stocks(self):
        _datas = defaultdict(lambda:(0,0))
        sku_stocks = Sku_Stock.stock_by_sku_id(self.id)
        for sku_stock in sku_stocks:
            _datas[sku_stock.store_id] = (sku_stock.quantity,sku_stock.order_quantity)
        return _datas

    def init_stocks(self):
        _sku_stocks = []
        for store_id in STORES.keys():
            sku_stock = Sku_Stock()
            sku_stock.sku_id = self.id
            sku_stock.store_id = store_id
            sku_stock.threshold = self.threshold
            _sku_stocks.append(sku_stock)
        db.session.add_all(_sku_stocks)

    @classmethod
    def get_by_id(cls,sku_id):
        return cls.query.get(sku_id)

    @property
    def actual_price(self):
        if self.discount_price > 0 and self.discount_price < self.price:
            return self.discount_price
        return self.price


    @property
    def property_list(self):
        result = []
        for p in SKU_PROPERTIES:
            if self.properties.has_key(p):
                result.append((SKU_PROPERTIES_NAME[p], self.properties[p]))
        return result


    @hybrid_property
    def actual_quantity(self):
        return self.quantity - self.order_quantity - self.loss_quantity

    @hybrid_property
    def quantity_flag(self):
        return self.quantity - self.order_quantity - self.loss_quantity - self.threshold


event.listen(Sku.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=10001;'))


class Sku_Stock(db.Model):
    '''商品库存'''

    __tablename__ = 'sku_stock'

    id = Column(db.Integer, primary_key=True)
    sku_id = Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)
    store_id = Column(db.SmallInteger, nullable=False)#所在库房
    quantity = Column(db.Integer(unsigned=True), default=0)#库存数量
    order_quantity = Column(db.Integer(unsigned=True), default=0)#销售数量
    threshold = Column(db.Integer(unsigned=True), default=0)#阀值

    sku = db.relationship('Sku', backref=db.backref('sku_stores', lazy='dynamic'))

    __table_args__ = (
        UniqueConstraint(sku_id,store_id),
    )

    @hybrid_property
    def actual_quantity(self):
        return self.quantity-self.order_quantity

    @classmethod
    def stock_by_sku_id(cls,sku_id):
        sku_stocks = cls.query.filter(cls.sku_id==sku_id)
        return sku_stocks

event.listen(Sku_Stock.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=100001;'))


class Loss(db.Model):
    '''商品报损明细表'''
    __tablename__ = 'loss'

    id = Column(db.Integer, primary_key=True)
    sku_id = Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)
    quantity = Column(db.Integer(unsigned=True), default=0)#报损数量
    channel = Column(db.SmallInteger,default=0)#损坏渠道（2:原厂损坏,3:库房损坏,4:发货途中,5:退货途中,1:不明原因）
    degree = Column(db.SmallInteger,default=0)#损坏程度（2:发霉,3:外包装损,4:破碎,1:其他）
    type = Column(db.SmallInteger, nullable=False, default=1)#报损类型（1:报损出库,2:出库）
    link_order_id = Column(db.BigInteger, db.ForeignKey('order.order_id'),nullable=True)#关联订单ID
    remark = Column(db.String(500))#报损备注
    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:未审批,2:待审批,9:已报损)
    created = Column(db.DateTime, default=datetime.now)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#隶属操作人员
    operator = db.relationship('Operator', backref=db.backref('losses', lazy='dynamic'))

    sku = db.relationship('Sku', backref=db.backref('loss_items', lazy='dynamic'))

    @property
    def channel_name(self):
        return LOSS_CHANNELS[self.channel]

    @property
    def degree_name(self):
        return LOSS_DEGREES[self.degree]

    @property
    def type_name(self):
        return LOSS_TYPES[self.type]

    @property
    def status_name(self):
        return LOSS_STATUS[self.status]


class Stock_In(db.Model):
    '''商品入库表'''

    __tablename__ = 'stock_in'

    id = Column(db.BigInteger,primary_key=True)
    code = Column(db.String(50))#凭证号
    c = Column(db.SmallInteger,nullable=False,index=True)#入库1级分类（10:采购入库,11:借调入库,20:退货入库）
    order_id = Column(db.BigInteger, db.ForeignKey('order.order_id'),nullable=True)#关联订单ID
    store_id = Column(db.SmallInteger, nullable=False)#所在库房
    sku_id = Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)
    quantity = Column(db.Integer(unsigned=True), default=0)#入库数量
    shelf_number = Column(db.String(50))#货架号
    made_in = Column(db.String(100))#产地
    mfg_date = Column(db.DateTime)#生产日期
    exp_date = Column(db.DateTime)#截止有效期
    purchase_price = Column(db.Float(unsigned=True), nullable=False,default=0)#进货价
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#隶属操作人员
    approver_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#审批人ID
    approval_time = Column(db.DateTime,nullable=True)
    created = Column(db.DateTime, default=datetime.now)#创建日期
    valid_time = Column(db.DateTime,nullable=True)#生效日期
    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:审批未通过,2:待审批,9:正常)
    remark = Column(db.String(500),nullable=True)#备注

    operator = db.relationship('Operator', primaryjoin="(Operator.id == Stock_In.operator_id)")
    approver = db.relationship('Operator', primaryjoin="(Operator.id == Stock_In.approver_id)")
    sku = db.relationship('Sku', backref=db.backref('stock_ins', lazy='dynamic'))
    order = db.relationship('Order', primaryjoin="(Order.order_id == Stock_In.order_id)")
    @property
    def sku_stock(self):
        _sku_stock = Sku_Stock.query.filter(Sku_Stock.store_id==self.store_id,Sku_Stock.sku_id==self.sku_id).first()
        return _sku_stock

    @property
    def property_list(self):
        _brief = []
        if self.code:
            _brief.append((u'入库凭证',self.code))
        if self.shelf_number:
            _brief.append((u'货架号',self.shelf_number))

        if self.mfg_date:
            _brief.append((u'生产日期',self.mfg_date.strftime('%Y.%m.%d')))

        if self.exp_date:
            _brief.append((u'有效期至',self.exp_date.strftime('%Y.%m.%d')))

        if self.made_in:
            _brief.append((u'产地',self.made_in))
        return _brief

    @property
    def c_name(self):
        return STOCK_IN_CATEGORIES[self.c]

    @property
    def status_name(self):
        return STOCK_STATUS[self.status]

    @classmethod
    def sale_return(cls,order_id,sku_id,quantity,store_id,remark=''):
        stock_sale_return = cls()
        stock_sale_return.c = 20
        stock_sale_return.order_id = order_id
        stock_sale_return.store_id = store_id
        stock_sale_return.sku_id = sku_id
        stock_sale_return.quantity = quantity
        stock_sale_return.operator_id = current_user.id
        stock_sale_return.remark = remark
        stock_sale_return.status = 9
        stock_sale_return.valid_time = datetime.now()
        db.session.add(stock_sale_return)

        Sku_Stock.query.filter(db.and_(Sku_Stock.store_id==store_id,
                                       Sku_Stock.sku_id==sku_id)).update({'quantity':Sku_Stock.quantity+quantity})
        return True,stock_sale_return

event.listen(Stock_In.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=1000000001;'))


class Stock_Out(db.Model):
    '''商品出库表'''
    __tablename__ = 'stock_out'
    id = Column(db.BigInteger,primary_key=True)
    code = Column(db.String(50))#凭证号
    c = Column(db.SmallInteger,nullable=False,index=True)#出库1级分类（10:销售出库,11:借调出库,13:客情出库,20:报损出库）
    order_id = Column(db.BigInteger, db.ForeignKey('order.order_id'),nullable=True)#关联订单ID
    store_id = Column(db.SmallInteger, nullable=False)#所在库房
    sku_id = Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)#商品ID
    quantity = Column(db.Integer(unsigned=True), default=0)#出库数量
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#操作员ID
    approver_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#审批人ID
    approval_time = Column(db.DateTime,nullable=True)
    created = Column(db.DateTime, default=datetime.now)#创建日期
    valid_time = Column(db.DateTime,nullable=True)#生效日期
    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:审批未通过,2:待审批,9:正常)
    remark = Column(db.String(500),nullable=True)#备注

    operator = db.relationship('Operator', primaryjoin="(Operator.id == Stock_Out.operator_id)")
    approver = db.relationship('Operator', primaryjoin="(Operator.id == Stock_Out.approver_id)")
    sku = db.relationship('Sku', backref=db.backref('stock_outs', lazy='dynamic'))

    @property
    def c_name(self):
        return STOCK_OUT_CATEGORIES[self.c]

    @property
    def sku_stock(self):
        _sku_stock = Sku_Stock.query.filter(Sku_Stock.store_id==self.store_id,Sku_Stock.sku_id==self.sku_id).first()
        return _sku_stock

    @property
    def status_name(self):
        return STOCK_STATUS[self.status]

    @classmethod
    def sale(cls,order,sku_id,quantity,store_id,remark=''):
        '''商品销售出库'''
        stock_sale = cls()
        stock_sale.c = ORDER_RELATED_STOCK_OUT_CATEGORIES.get(order.order_type,10)
        stock_sale.order_id = order.order_id
        stock_sale.store_id = store_id
        stock_sale.sku_id = sku_id
        stock_sale.quantity = quantity
        stock_sale.operator_id = current_user.id
        stock_sale.remark = remark
        stock_sale.status = 9
        stock_sale.valid_time = datetime.now()
        db.session.add(stock_sale)
        return True,stock_sale

event.listen(Stock_Out.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=2000000001;'))


class Stock_Inventory(db.Model):
    '''库存盘点表'''

    __tablename__ = 'stock_inventory'

    id = Column(db.Integer, primary_key=True)
    sku_id = Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)
    store_id = Column(db.SmallInteger, nullable=False)#所在库房
    ins = Column(fields.Dict(500),nullable=True)
    in_quantity = Column(db.Integer,nullable=False,default=0)
    outs = Column(fields.Dict(500),nullable=True)
    out_quantity = Column(db.Integer,nullable=False,default=0)
    quantity = Column(db.Integer,nullable=False,default=0)
    date = Column(db.Date,nullable=False)



class Stock(db.Model):
    '''库存'''

    __tablename__ = 'stock'

    id = Column(db.Integer, primary_key=True)
    sku_id = Column(db.Integer, db.ForeignKey('sku.id'), nullable=False)
    store_id = Column(db.SmallInteger, nullable=False)#所在库房
    shelf_number = Column(db.String(50))#货架号
    code = Column(db.String(50))#条码号
    made_in = Column(db.String(100))#产地
    purchase_price = Column(db.Float(unsigned=True), nullable=False)#进货单价
    mfg_date = Column(db.DateTime, default=datetime.now)#生产日期
    exp_date = Column(db.DateTime, default=datetime.now)#截止有效期
    in_quantity = Column(db.Integer(unsigned=True), default=0)#入库数量
    out_quantity = Column(db.Integer(unsigned=True), default=0)#出货数量
    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:未审批,2:待财务审批,9:正常)
    log = Column(db.String(50), nullable=True)
    ext_fields = Column(fields.Dict(500))#扩展信息
    created = Column(db.DateTime, default=datetime.now)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#隶属操作人员
    remark = Column(db.String(500),nullable=True)
    operator = db.relationship('Operator', backref=db.backref('stocks', lazy='dynamic'))

    # sku = db.relationship('Sku', backref=db.backref('stocks', lazy='dynamic'))

    @property
    def status_name(self):
        return STOCK_STATUS[self.status]

    @hybrid_property
    def quantity(self):
        return self.in_quantity - self.out_quantity

    @classmethod
    def stock_by_sku_id(cls, sku_id, min_quantity=1):
        try:
            return cls.query.filter(db.and_(cls.quantity >= min_quantity, cls.sku_id == sku_id, cls.status==9)).order_by(
                cls.exp_date).first()
        except Exception, e:
            return None


class Store(db.Model):
    '''库房'''
    __tablename__ = 'store'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(50), nullable=False)
    address = Column(db.String(200), nullable=False)
    ext_fields = Column(fields.Dict(500))#扩展信息

    #stocks = db.relationship('Stock', backref='store', lazy='dynamic')


class IO_Log(db.Model):
    '''出入库日志'''

    __tablename__ = 'io_log'

    id = Column(db.BigInteger, primary_key=True)
    sku_id = Column(db.ForeignKey('sku.id'), nullable=False)
    stock_id = Column(db.ForeignKey('stock.id'), nullable=True)
    type = Column(db.SmallInteger, nullable=False)#(10:进货入库,11:退货入库,20:订单出库,21:报损出库,22:借贷出库)
    quantity = Column(db.Integer(unsigned=True), nullable=False, default=0)#数量
    order_id = Column(db.BigInteger, db.ForeignKey('order.order_id'),nullable=True)#关联订单ID
    ext_fields = Column(fields.Dict(500))#扩展信息
    created = Column(db.DateTime, default=datetime.now)

    @classmethod
    def add(cls,sku_id,stock_id,type,quantity,order_id=None,ext_fields={}):
        io_log = IO_Log()
        io_log.sku_id = sku_id
        io_log.stock_id = stock_id
        io_log.type = type
        io_log.quantity = quantity
        io_log.order_id = order_id
        io_log.ext_fields = ext_fields
        db.session.add(io_log)
        #db.session.flush()
        return io_log


############################
#   用户模块
############################
class ChinaAddress(db.Model):
    __tablename__ = 'china_address'

    region_id = Column(db.Integer, primary_key=True)
    parent_id = Column(db.Integer, db.ForeignKey('china_address.region_id'), nullable=False)
    region_name = Column(db.String(50), nullable=False)
    region_type = Column(db.SmallInteger, nullable=False)
    agency_id = Column(db.SmallInteger)


class User(db.Model):
    '''用户信息表'''

    __tablename__ = 'user'

    user_id = Column(db.Integer, primary_key=True)
    name = Column(db.String(50), nullable=False)
    gender = Column(db.String(10), nullable=False, default=u'保密')#性别
    phone = Column(db.String(15), nullable=False, unique=True)#手机号
    phone2 = Column(db.String(15), nullable=False, unique=True)#手机号2
    tel = Column(db.String(25))#电话号码
    tel2 = Column(db.String(25))#电话号码2
    user_type = Column(db.SmallInteger(unsigned=True),nullable=False,default=1)#客户类型 -> (1:新客户、2:会员客户、4:黑名单)
    label_id = Column(db.SmallInteger(unsigned=True),nullable=False,default=1)#客户标签
    batch_id = Column(db.String(50))#用户特殊标签
    birthday = Column(db.Date)#生日
    ages = Column(db.SmallInteger(unsigned=True),nullable=False,default=0)###客户年龄段
    profession = Column(db.String(50))#职业
    income = Column(db.SmallInteger(unsigned=True),nullable=False,default=0)#收入
    concerns = Column(fields.List(200),nullable=True)####关心问题

    m1 = Column(db.String(50),nullable=True)###媒体来源 - 1级
    m2 = Column(db.String(50),nullable=True)###媒体来源 - 2级
    m3 = Column(db.String(50),nullable=True)###媒体来源 - 3级

    order_fee = Column(db.Float(unsigned=True),nullable=False,default=0)#订单费用
    order_num = Column(db.Integer,nullable=False,default=0)#订单数

    total_fee = Column(db.Integer, nullable=False, default=0)#累计积分
    used_fee = Column(db.Integer, nullable=False, default=0)#已用积分
    grade = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#客户等级
    intent_level = Column(db.String(2),nullable=False,default='A')#意向等级
    origin = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#来源
    email = Column(db.String(50))#邮箱地址
    remark = Column(db.String(500))#备注
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#初始操作人员

    assign_operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#当前分配人员
    assign_time = Column(db.DateTime,default=datetime.now)#分配时间
    assign_retain_time = Column(db.SmallInteger,nullable=False,default=0)#分配保留时间（单位:小时）
    is_assigned = Column(db.Boolean,nullable=False,default=False)#是否已分配
    is_abandon = Column(db.Boolean,nullable=False,default=False)#是否被放弃
    is_sms = Column(db.Boolean,nullable=False,default=False)#是否发送短信
    expect_time = Column(db.DateTime,nullable=True)#预约时间

    product_intention=Column(db.SmallInteger(unsigned=True), nullable=True)#产品意向add john 20131120
    member_time = Column(db.Date,nullable=True)#成为会员客户的时间add john 20131120

    dialog_times = Column(db.SmallInteger,nullable=False,default=0)#沟通次数
    last_dialog_time = Column(db.DateTime,default=datetime.now)#最后一次沟通时间

    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#当前状态(1:正常,2:冻结)
    join_time = Column(db.DateTime, default=datetime.now)#加入日期
    ext_fields = Column(fields.Dict(500))#扩展信息
    #entries = deferred(Column(fields.Json(3000)))
    
    #habits_customs = Column(db.String(500))#生活习惯
    
    addresses = db.relationship('Address', backref='user', lazy='dynamic')
    #dialogs = db.relationship('User_Dialog', backref='user', lazy='dynamic')
    
    #qxhkhdjs = db.relationship('QXHKHDJ', backref='user', lazy='dynamic')

    operator = db.relationship('Operator', primaryjoin="(Operator.id == User.operator_id)")
    assign_operator = db.relationship('Operator', primaryjoin="(Operator.id == User.assign_operator_id)")
    qxhdm_time = Column(db.Date)#录入时间
    qxhdm_user_id = Column(db.Integer)#
    is_valid = Column(db.SmallInteger(unsigned=True), nullable=False, default=0)#是否有效1有效，2无效,3无法确认
    is_new = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#是否新客户
    fugou = Column(db.SmallInteger(unsigned=True), nullable=False, default=0)#

    record_time = Column(db.Date)#最后录音时间
    user_label = Column(db.SmallInteger(unsigned=True), nullable=False, default=1)#1常规,2会员,3激活
    hy_time = Column(db.Date)#成为会员时间
    lastfugou_time = Column(db.Date)#最后复购时间
    fugou_bigcount = Column(db.Integer(unsigned=True), default=0)#复购大数量
    fugou_mediumcount = Column(db.Integer(unsigned=True), default=0)#复购中数量
    fugou_smallcount = Column(db.Integer(unsigned=True), default=0)#复购小数量
    is_isable = Column(db.Integer(unsigned=True), default=0)#是否停用
    isable_reason = Column(db.String(50))#原因
    purchases = Column(db.String(500))#购买情况
    disease = Column(db.String(500))#病症
    promoters = Column(db.String(20))#促销员
    area = Column(db.String(20))#区域
    pharmacy = Column(db.String(50))#药房
    pharmacystores = Column(db.String(50))#分店
    
    weixin = Column(fields.List(20),nullable=True)#微信情况
    orgin = Column(fields.List(300),nullable=True)#身体状态
    orgina = Column(db.String(300))#身体状态病症
    orginb = Column(db.String(300))#身体状态病症
    orginc = Column(db.String(300))#身体状态病症
    orgind = Column(db.String(300))#身体状态病症
    orgine = Column(db.String(300))#身体状态病症
    history = Column(db.String(300))#身体状态病症
    
    communication = Column(db.String(30))#沟通情况
    
    dlb_time = Column(db.Date)#大礼包时间
    dlb_type = Column(db.SmallInteger(unsigned=True), nullable=False, default=0)#大礼包类型1留言，2微信
    dlb_valid = Column(db.SmallInteger(unsigned=True), nullable=False, default=0)#大礼包是否有效1有效，2无效
    dlb_new = Column(db.SmallInteger(unsigned=True), nullable=False, default=0)#大礼包是否新客户1新，2老
    dlb_connect = Column(db.SmallInteger(unsigned=True), nullable=False, default=0)#大礼包是否接通1接通，2不通
    @property
    def mobile_phones(self):
        _phones = []
        for p in (self.phone,self.phone2,self.tel,self.tel2):
            if p and len(p)==11 and p.startswith('1') and not p.startswith('10'):
                _phones.append(p)
        return ','.join(set(_phones))

    @hybrid_property
    def _phone(self):
        return '%s****%s'%(self.phone[:3],self.phone[7:]) if self.phone else ''

    @hybrid_property
    def _phone2(self):
        return '%s****%s'%(self.phone2[:3],self.phone2[7:]) if self.phone2 else ''

    @hybrid_property
    def _tel(self):
        return '%s****%s'%(self.tel[:3],self.tel[7:]) if self.tel else ''

    @hybrid_property
    def _tel2(self):
        return '%s****%s'%(self.tel2[:3],self.tel2[7:]) if self.tel2 else ''

    @property
    def phones(self):
        if current_user and current_user.action('view_user_phone'):
            return [p for p in (self.phone,self.phone2) if p]
        return [p for p in (self._phone,self._phone2) if p]

    @property
    def tels(self):
        if current_user and  current_user.action('view_user_phone'):
            return [p for p in (self.tel,self.tel2) if p]
        return [p for p in (self._tel,self._tel2) if p]

    @property
    def user_token(self):
        return des.user_token(self.user_id)

    @property
    def label(self):
        if self.user_type == 1:
            if self.order_num>0:return u'已下单'
            return USER_LABEL_IDS.get(self.label_id,u'')
        return u''

    def add_order(self,order):
        self.order_num = User.order_num + 1
        self.order_fee = User.order_fee + order.actual_fee

    def del_order(self,order):
        if self.user_type==1:
            self.label_id = ORDER_STATUS_RELATED_USER_LABEL.get(order.status,1)

        if self.assign_operator_id and self.assign_retain_time>0 and self.user_type == 1 and self.order_num==1 and order.status == 104:#拒收订单操作
            self.assign_time = datetime.now()
            self.assign_retain_time = 24

        self.order_num = User.order_num - 1
        self.order_fee = User.order_fee - order.actual_fee


    @property
    def is_authorize(self):
        if not current_user:return False
        if current_user.id==self.assign_operator_id:#current_user.is_admin or
            return True

        if self.assign_operator_id>0 and current_user.action('manage_users') and current_user.team and self.assign_operator.team and self.assign_operator.team.startswith(current_user.team):
            return True

        return False

    @property
    def assign_remain_info(self):
        if self.assign_operator_id and self.assign_retain_time>0 and self.order_num==0:
            expired = self.assign_time+timedelta(hours=self.assign_retain_time)
            now = datetime.now()
            return converse_s_2_dhms_zh(delta_s(expired,now)) if expired>now else u'已到期'
        return '-'

    @property
    def type_name(self):
        if self.user_type==1:return u'新客户'
        if self.user_type==2:return u'会员客户'
        if self.user_type==4:return u'黑名单'
        if self.user_type==5:return u'服务客户'
        return u''

    @hybrid_property
    def fee(self):
        return self.total_fee - self.used_fee

    @property
    def sms_message(self):
        if self.assign_operator_id:
            return u'尊敬的%s，我是您的健康医师：%s医师，工号：%s；您有任何的问题，欢迎随时来电咨询我。服务热线：4006002000【爱妻美】'%(self.name,self.assign_operator.nickname[:1],self.assign_operator.op_id)
        return ''

    def retain_time(self,team):
        if TEAM_RETAIN_USER_HOURS.has_key(team):
            _team_retain_hours = TEAM_RETAIN_USER_HOURS[team]
            return _team_retain_hours[self.origin] if _team_retain_hours.has_key(self.origin) else _team_retain_hours[0]
            return TEAM_RETAIN_DEFAULT_HOURS if self.user_type == 1 else 0

    def assign_op(self,op,operator_id,is_abandon=False,allowed_change_user_type=True):
        self.assign_time = datetime.now()
        if not op:
            self.assign_operator_id = None
            self.assign_retain_time = 0
        else:
            
            #---> 修改客户类型
            if allowed_change_user_type and (not op.assign_user_type&self.user_type) and op.assign_user_type:
                self.user_type = op.assign_user_type

            self.assign_operator_id = op.id
            self.is_assigned = True
            self.assign_retain_time = self.retain_time(op.team)#USER_ASSIGN_HOURS.get(self.origin,ASSIGN_DEFAULT_HOURS)
            # if self.user_type == 1:
            #
            # else:
            #     self.assign_retain_time = 0

            if self.user_type == 2:
                self.is_sms = False

        assign_log = User_Assign_Log()
        assign_log.user_id = self.user_id
        assign_log.assign_operator_id = op.id if op else None
        assign_log.operator_id = operator_id
        assign_log.user_type = self.user_type
        assign_log.is_abandon = is_abandon
        assign_log.ip = request.remote_addr
        db.session.add(assign_log)


event.listen(User.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=10000001;'))


class User_Giveup(db.Model):

    __tablename__ = 'user_giveup'

    id = Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', primaryjoin="(User.user_id == User_Giveup.user_id)")
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#操作员
    created = Column(db.DateTime, default=datetime.now)
    audit_operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#审核操作员
    audit_time = Column(db.DateTime, default=datetime.now)#操作时间
    status = Column(db.Integer, default=0)#状态1通过,2未通过
    reason = Column(db.String(150))#原因
    remarks = Column(db.String(150))#备注

class User_Entry(db.Model):

    __tablename__ = 'user_entry'

    id = Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    code = db.Column(db.String(10),nullable=False,default=False)
    c1 = db.Column(db.String(50))#类别1
    c2 = db.Column(db.String(50))#类别2
    c3 = db.Column(db.String(50))#类别3
    value = db.Column(db.String(500))
    created = Column(db.DateTime, default=datetime.now)



class User_Assign_Log(db.Model):

    __tablename__ = 'user_assign_log'

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('user.user_id'))
    user_type = Column(db.SmallInteger(unsigned=True),nullable=False,default=1)#客户类型 -> (1:新客户、2:会员客户、4:黑名单)
    assign_operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#当前分配人员
    assign_time = Column(db.DateTime,default=datetime.now)#分配时间
    is_abandon = Column(db.Boolean,nullable=False,default=False)#是否被放弃
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#操作人员
    operator = db.relationship('Operator', primaryjoin="(Operator.id == User_Assign_Log.operator_id)")
    assign_operator = db.relationship('Operator', primaryjoin="(Operator.id == User_Assign_Log.assign_operator_id)")
    ip = Column(db.String(30))#ip

    @property
    def user_type_name(self):
        return USER_TYPES[self.user_type]

    @property
    def message(self):
        _msg = ''
        if self.operator_id:
            _msg += u'经由<span style="color:blue">%s</span>'%self.operator.nickname


        user_type_name = USER_TYPES[self.user_type]
        if self.assign_operator_id:
            _msg += u'分配给<span style="color:red">%s</span>'%self.assign_operator.nickname
        else:
            if self.is_abandon:
                _msg += u'放弃了'
            else:
                _msg += u'进入%s公共库'%user_type_name

        _msg += u' (%s) %s'%(user_type_name,self.assign_time.strftime('%Y-%m-%d %H:%M:%S'))
        return _msg


class User_Phone(db.Model):

    __tablename__ = 'user_phone'

    id = Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    phone = Column(db.String(15), nullable=False, unique=True)
    #province = Column(db.String(50),nullable=True)

    @classmethod
    def add_phone(cls,user_id,phone):
        user_phone = cls()
        user_phone.user_id = user_id
        user_phone.phone = phone
        return user_phone

    @classmethod
    def user_id_by_phone(cls,phone_number):
        obj = cls.query.filter(cls.phone==phone_number).first()
        if obj:return obj.user_id
        return 0


class User_Dialog(db.Model):
    '''客户联系记录表'''

    __tablename__ = 'user_dialog'

    id = Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    solution = db.Column(db.String(1000))
    record_number = db.Column(db.String(50))
    type = db.Column(db.SmallInteger,nullable=False,default=1)#--->DIALOG_TYPES
    content = db.Column(db.Text)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)
    operator = db.relationship('Operator', backref=db.backref('dialogs', lazy='dynamic'))
    created = Column(db.DateTime, default=datetime.now)

    @classmethod
    def add_dialog(cls,op_id,user_id,solution,type,content,record_number):
        obj = cls()
        obj.user_id = user_id
        obj.operator_id = op_id
        obj.solution = solution
        obj.record_number = record_number
        obj.type = type
        obj.content = content
        if record_number:
            User.query.filter(User.user_id==user_id).update({'dialog_times':User.dialog_times+1,'last_dialog_time':datetime.now(),'record_time':datetime.now()})
        else:
            User.query.filter(User.user_id==user_id).update({'dialog_times':User.dialog_times+1,'last_dialog_time':datetime.now()})
        return obj


import urllib2,urllib
import xml.etree.ElementTree as ET
from collections import namedtuple

SMS_RESPONSE = namedtuple('sms_response','error message')
def sms_repsonse(error=-1,message=''):
    return SMS_RESPONSE(error=int(error),message=message)

class SMS(db.Model):
    '''短信发送日志表'''

    __tablename__ = 'sms'

    seqid = Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=True)
    phone = db.Column(db.String(5000),nullable=False)
    message = db.Column(db.String(500),nullable=False)
    sendtime = db.Column(db.DateTime,nullable=True)
    addserial = db.Column(db.String(10),nullable=False,default='')#短信附加号
    priority = db.Column(db.SmallInteger(unsigned=True),nullable=False,default=1)
    fail_times = db.Column(db.SmallInteger(unsigned=True),nullable=False,default=0)#失败次数
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)
    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=0)#当前状态(0:待审批,1:待发送,2:发送成功,9:发送失败)
    created = Column(db.DateTime, default=datetime.now)
    operate_time = Column(db.DateTime,nullable=True)

    remark = Column(db.String(100))#备注

    user = db.relationship('User', primaryjoin="(User.user_id == SMS.user_id)")
    operator = db.relationship('Operator', backref=db.backref('sms_list', lazy='dynamic'))

    @property
    def status_name(self):
        return SMS_STATUS[self.status]


    @classmethod
    def add_sms(cls,phone,message,sendtime,addserial='',status=0,priority=1,operator_id=None,user_id=None,remark='',commit=True):
        _sms = SMS()
        _sms.phone = phone
        _sms.message = message
        _sms.sendtime = sendtime
        _sms.addserial = addserial
        _sms.priority = priority
        _sms.operator_id = operator_id
        _sms.user_id = user_id
        _sms.status = status
        _sms.remark = remark
        db.session.add(_sms)
        if commit:db.session.commit()
        return _sms

    @staticmethod
    def response(data):
        try:
            root = ET.fromstring(data.replace('\n','').replace('\r',''))
            res = {}
            for child in root:
                res[child.tag] = child.text
            return sms_repsonse(**res)
        except Exception,e:
            print 'happen error:%s'%e
            return sms_repsonse()

    def send_sms(self):
        '''短信发送操作'''
        if self.status == 2:return True
        params_data = urllib.urlencode(self.send_params)
        f = urllib2.urlopen(self.url,data=params_data,timeout=30)
        print params_data
        data = f.read()
        res = SMS.response(data)
        result = False
        if res.error == 0:#发送成功
            self.status = 2
            self.operate_time = datetime.now()
            result = True
        else:
            self.status = 9
            self.fail_times = SMS.fail_times + 1
            current_app.logger.error('SEND_SMS_FAIL|%s|%s|%s|%s' % (self.seqid,self.phone,res.error,res.message))
        db.session.commit()
        return result

    @property
    def send_params(self):
        params = {'cdkey':SMS_CDKEY,
                  'password':SMS_PASSWORD,
                  'phone':self.phone,
                  'message':self.message,#.replace('=','').replace('&',''),
                  'addserial':self.addserial,
                  'smspriority':self.priority,
                  'seqid':self.seqid}
        if self.sendtime:
            params['sendtime'] = self.sendtime.strftime('%Y%m%d%H%M%S')#格式为:年年年年月月日日时时分分秒秒,例如:20090504111010
        return params

    @property
    def url(self):
        return SEND_TIME_SMS_URI if self.sendtime else SEND_SMS_URI


class Address(db.Model):
    '''地址信息表'''

    __tablename__ = 'address'

    id = Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    ship_to = Column(db.String(50), nullable=False)#收货人姓名
    tel = Column(db.String(15))#联系电话
    phone = Column(db.String(15))#电话号码
    province = Column(db.String(20))#省份
    city = Column(db.String(20))#城市
    district = Column(db.String(20))#所在区
    street1 = Column(db.String(100))#街道1
    street2 = Column(db.String(100))#街道2
    postcode = Column(db.String(50))#邮政编码
    email = Column(db.String(50))#邮箱地址
    is_default = Column(db.Boolean,nullable=False,default=False)#是否为默认地址
    # created = Column(db.DateTime, default=datetime.now)#创建日

    @property
    def mobile_phones(self):
        _phones = []
        for p in (self.phone,self.tel):
            if p and len(p)==11 and p.startswith('1') and not p.startswith('10'):
                _phones.append(p)
        return ','.join(set(_phones))

    @property
    def format_address(self):
        _str = ''
        for s in (self.province, self.city, self.district, self.street1, self.street2):
            if s and s <> u'市辖区' and s <> u'县辖区':
                _str += s
        return _str


############################
#   权限模块
############################
class Operator(db.Model, UserMixin):
    '''操作人员信息表'''

    __tablename__ = 'operator'

    id = Column(db.Integer, primary_key=True)
    nickname = Column(db.String(50), nullable=False)
    email = Column(db.String(50))
    team = Column(db.String(5),nullable=True,index=True)
    username = Column(db.String(50), nullable=False, unique=True)
    op_id = Column(db.String(10),nullable=True)#工号
    _password = Column('password', db.String(80), nullable=False)
    created = Column(db.DateTime, default=datetime.now)
    store_id = Column(db.SmallInteger, nullable=False)#所在库房
    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password,method='sha1')

    password = db.synonym('_password', descriptor=property(_get_password, _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    role_id = Column(db.ForeignKey('role.id'), nullable=False)#角色ID
    is_admin = Column(db.Boolean, nullable=False, default=False)#是否为管理员
    assign_orders = Column(db.Integer,nullable=False,default=0)#分配订单数
    assign_user_type = Column(db.SmallInteger(unsigned=True),default=0)#指派客户类型
    status = Column(db.SmallInteger(unsigned=True), nullable=False, default=2)#当前状态(1:上班,2:下班,9:冻结)

    role = db.relationship('Role', backref='operators',lazy=False)

    @classmethod
    def operators_by_user_type(cls,user_type):
        return cls.query.filter('`assign_user_type`&%s'%user_type)

    @property
    def assign_users(self):
        _users = []
        if self.assign_user_type&1:
            _users.append(u'新客户')
        if self.assign_user_type&2:
            _users.append(u'会员客户')
        if self.assign_user_type&5:
            _users.append(u'会员服务')
        return _users

    @property
    def status_name(self):
        return OPERATOR_STATUS[self.status]

    @property
    def role_name(self):
        return self.role.name

    @property
    def team_fullname(self):
        if self.team:
            if len(self.team)==2:
                return '%s -> %s'%(DEPARTMENTS[self.team[0]],TEAMS[self.team])
            elif len(self.team) == 1:
                return DEPARTMENTS[self.team]
        return '-'

    def action(self, action_name):
        if self.is_admin or action_name in self.role.endpoints:
            return True
        return False

    def allowed_order_action(self, order_status, required_operator=0):
        if self.is_admin: return True
        if required_operator and required_operator <> self.id: return False
        if order_status in ROLE_ALLOWED_ORDER_STATUS.get(self.role_id, []):
            return True
        return False

    @classmethod
    def authenticate(cls, login, password):
        operator = cls.query.filter(cls.username == login).first()
        if operator:
            if operator.status == 9:
                authenticated = False
            else:
                authenticated = operator.check_password(password)#True#
        else:
            authenticated = False
        return operator, authenticated


ROLE_ENDPOINTS = {}
class Role(db.Model):

    __tablename__ = 'role'

    id = Column(db.Integer,primary_key=True)
    name = Column(db.String(20),nullable=False,unique=True)
    endpoints = Column(fields.List(5000))


event.listen(Role.__table__, 'after_create', DDL('ALTER TABLE %(table)s AUTO_INCREMENT=101;'))


# class Permission(db.Model):
#     '''权限配置表'''
#
#     __tablename__ = 'permission'
#
#     id = Column(db.Integer, primary_key=True)
#     endpoint = Column(db.String(30), nullable=False)#节点
#     uri = Column(db.String(20), nullable=False,unique=True)#URI
#
#
# class Role(db.Model):
#     '''角色配置表'''
#     __tablename__ = 'role'
#
#     id = Column(db.Integer, primary_key=True)
#     name = Column(db.String(20), nullable=False,unique=True)#角色名称
#     perm_ids = Column(fields.List(500))#权限列表
#
#     def _get_perms(self):
#         return Permission.query.filter(Permission.id.in_(self.perm_ids or set()))
#     def _set_perms(self, perms):
#         self.perm_ids = [p.id for p in perms]
#     permissions = db.synonym('perm_ids',descriptor=property(_get_perms,_set_perms))
#
#     operators = db.relationship('Operator', backref='role', lazy='dynamic')


class News(db.Model):
    '''信息表'''
    __tablename__ = 'news'

    id = Column(db.Integer, primary_key=True)
    title = Column(db.String(200), nullable=False)#标题
    content = Column(db.Text)#内容
    created = Column(db.DateTime, default=datetime.now)

class Security_Code(db.Model):
    '''防伪码'''
    __tablename__ = 'security_code'

    id = Column(db.Integer, primary_key=True)
    code = Column(db.String(8), nullable=False, unique=True)
    #created = Column(db.DateTime, nullable=False, default=datetime.now)

class Security_Code_Log(db.Model):
    '''防伪码查询记录'''
    __tablename__ = 'security_code_log'

    id = Column(db.Integer, primary_key=True)
    code = Column(db.String(8), nullable=False)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)
    operator = db.relationship('Operator', primaryjoin="(Operator.id == Security_Code_Log.operator_id)")
    username = Column(db.String(20))#姓名
    tel = Column(db.String(20))#电话
    province = Column(db.String(20))#省
    city = Column(db.String(20))#市
    district = Column(db.String(20))#地区
    street = Column(db.String(20))#街道
    created = Column(db.DateTime, default=datetime.now)
    ip = Column(db.String(30))#ip

class Order_LHYD_Postal(db.Model):
    '''陆航韵达 邮政单号'''
    __tablename__ = 'order_lhyd_postal'

    #id = Column(db.Integer, primary_key=True)Column(db.BigInteger(unsigned=True), primary_key=True, autoincrement=False)
    order_id = Column(db.BigInteger(unsigned=True), db.ForeignKey('order.order_id'), primary_key=True, autoincrement=False)
    express_id = Column(db.SmallInteger, nullable=False, default=5)#快递公司
    express_number = Column(db.String(50), index=True)#快递号
    
class User_Statistics(db.Model):
    '''会员客户数据统计'''
    __tablename__ = 'user_statistics'

    tjdate = Column(db.Date, primary_key=True)
    new_users = Column(db.BigInteger(unsigned=True), nullable=True)#新进会员数
    giveup_users = Column(db.BigInteger(unsigned=True), nullable=True)#放弃客户数
    users = Column(db.BigInteger(unsigned=True), nullable=True)#会员客户总数
    hg_users = Column(db.BigInteger(unsigned=True), nullable=True)#回购客户数
    cm_users = Column(db.BigInteger(unsigned=True), nullable=True)#沉默客户数
    tj_users = Column(db.BigInteger(unsigned=True), nullable=True)#会员推荐数
    city_users = Column(db.BigInteger(unsigned=True), nullable=True)#市级客户数
    xian_users = Column(db.BigInteger(unsigned=True), nullable=True)#县级客户数
    hg_user_list = Column(db.Text)#回购客户列表
    cm_user_list = Column(db.Text)#沉默客户列表


class Knowledge_Category(db.Model):
    '''知识类别'''
    __tablename__ = 'knowledge_category'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(50))#类别名称
    status = Column(db.Boolean, nullable=False, default=True)
    
class Knowledge(db.Model):
    '''知识'''
    __tablename__ = 'knowledge'

    id = Column(db.Integer, primary_key=True)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)
    operator = db.relationship('Operator', primaryjoin="(Operator.id == Knowledge.operator_id)")
    category_id = Column(db.Integer, db.ForeignKey('knowledge_category.id'), nullable=False)
    category = db.relationship('Knowledge_Category', primaryjoin="(Knowledge_Category.id == Knowledge.category_id)")
    title = Column(db.String(50), nullable=False)#标题
    content = Column(db.Text, nullable=False)#内容
    created = Column(db.DateTime, default=datetime.now, nullable=False)
    

class Outbound(db.Model):
    '''外呼统计'''
    __tablename__ = 'outbound'

    id = Column(db.BigInteger(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    created = Column(db.DateTime, default=datetime.now, nullable=False)
    

class Order_Operator(db.Model):
    ''''''
    __tablename__ = 'order_operator'
    id = Column(db.Integer, primary_key=True)
    order_id = Column(db.BigInteger(unsigned=True), db.ForeignKey('order.order_id'), nullable=False)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)
    operate_time = Column(db.DateTime, default=datetime.now)
    to_operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)
    remark = Column(db.String(100))#备注
    ip = Column(db.String(30))#ip

    

class User_Voucher(db.Model):
    '''代金卷'''
    __tablename__ = 'user_voucher'

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('user.user_id'))
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#操作人员
    operator = db.relationship('Operator', primaryjoin="(Operator.id == User_Voucher.operator_id)")#操作人员
    created = Column(db.DateTime,default=datetime.now)#创建时间
    price = Column(db.Integer)#金额
    remark = Column(db.String(100))#备注
    status = Column(db.Boolean,nullable=False,default=False)#状态
    order_id = Column(db.BigInteger(unsigned=True), db.ForeignKey('order.order_id'), nullable=True)#订单号
    order = db.relationship('Order', primaryjoin="(Order.order_id == User_Voucher.order_id)")#订单

class QXHDM_Orderyf(db.Model):
    '''地面预判断订单'''
    __tablename__ = 'qxhdm_orderyf'
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)#重复
    dm_user_id = Column(db.Integer, nullable=False)#地面
    user = relationship('User', primaryjoin="(User.user_id == QXHDM_Orderyf.user_id)")
    bigcount = Column(db.Integer(unsigned=True), default=0)#大数量
    mediumcount = Column(db.Integer(unsigned=True), default=0)#中数量
    smallcount = Column(db.Integer(unsigned=True), default=0)#小数量
    qizaocount = Column(db.Integer(unsigned=True), default=0)#芪枣数量
    created = Column(db.DateTime, default=datetime.now, nullable=False)

class Security_Codekh(db.Model):
    '''气血和编码'''
    __tablename__ = 'security_codekh'

    id = Column(db.Integer, primary_key=True)
    code = Column(db.String(10), nullable=False, unique=True)
    qxhkjdj_id = Column(db.Integer, db.ForeignKey('qxhkjdj.id'))
    #qxhkjdj = relationship('QXHKHDJ', primaryjoin="(QXHKHDJ.id == Security_Codekh.qxhkjdj_id)")

class QXHKHDJ(db.Model):
    '''气血和空盒登记'''
    __tablename__ = 'qxhkjdj'
    
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)#重复
    user = relationship('User', primaryjoin="(User.user_id == QXHKHDJ.user_id)")
    date = Column(db.Date)
    qxhcode = Column(db.String(100), nullable=False)
    giftname = Column(db.String(100), nullable=False)
    giftcount = Column(db.Integer(unsigned=True), default=0)#礼品数量
    province = Column(db.String(20))#省份
    city = Column(db.String(20))#城市
    district = Column(db.String(20))#所在区
    pharmacyaddress = Column(db.String(100), nullable=False)
    qxhcodes = relationship('Security_Codekh', backref='qxhkjdj', lazy='dynamic')
    receive = Column(db.Integer,nullable=False,default=0)#状态是否领取
    status = Column(db.Boolean,nullable=False,default=True)#状态是否有效
    reason = Column(db.String(30))#原因


class User_Isable(db.Model):

    __tablename__ = 'user_isable'

    id = Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', primaryjoin="(User.user_id == User_Isable.user_id)")
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#操作员
    created = Column(db.DateTime, default=datetime.now)
    audit_operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=True)#审核操作员
    audit_time = Column(db.DateTime, default=datetime.now)#操作时间
    status = Column(db.Integer, default=0)#状态1通过,2未通过
    reason = Column(db.String(150))#原因
    is_isable = Column(db.Integer(unsigned=True), default=0)#是否停用
    remarks = Column(db.String(150))#备注

class User_tjfg(db.Model):
    '''服务推荐复购'''
    __tablename__ = 'user_tjfg'
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)#重复
    dm_user_id = Column(db.Integer, nullable=False)#地面
    user = relationship('User', primaryjoin="(User.user_id == User_tjfg.user_id)")
    bigcount = Column(db.Integer(unsigned=True), default=0)#大数量
    mediumcount = Column(db.Integer(unsigned=True), default=0)#中数量
    smallcount = Column(db.Integer(unsigned=True), default=0)#小数量
    qizaocount = Column(db.Integer(unsigned=True), default=0)#芪枣数量
    created = Column(db.DateTime, default=datetime.now, nullable=False)


class Weihu(db.Model):
    '''维护'''
    __tablename__ = 'report_weihu'

    id = Column(db.Integer, primary_key=True)
    date = Column(db.Date, nullable=False)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#操作员
    operator = db.relationship('Operator', primaryjoin="(Weihu.operator_id == Operator.id)")
    usercount = Column(db.Integer, default=0, nullable=False)#用户量
    usersales = Column(db.Integer, default=0, nullable=False)#业绩
    last_usercount = Column(db.Integer, default=0, nullable=False)#上月用户量
    last_usersales = Column(db.Integer, default=0, nullable=False)#上月业绩
    callusers = Column(db.Integer, default=0, nullable=False)#拨打数据
    nocallusers = Column(db.Integer, default=0, nullable=False)#未拨打数据
    silenceusers = Column(db.Integer, default=0, nullable=False)#沉默用户量
    newusers = Column(db.Integer, default=0, nullable=False)#新进用户量
    giveupusers = Column(db.Integer, default=0, nullable=False)#放弃用户量
    ordercount = Column(db.Integer, default=0, nullable=False)#订单数
    tuihuoorders = Column(db.Integer, default=0, nullable=False)#退货订单数
    tuihuosales = Column(db.Integer, default=0, nullable=False)#退货总额
    yaopinsales = Column(db.Integer, default=0, nullable=False)#药品业绩
    baojianpinsales = Column(db.Integer, default=0, nullable=False)#保健品业绩
    huazhuangpinsales = Column(db.Integer, default=0, nullable=False)#化妆品业绩

class Waihu(db.Model):
    '''外呼'''
    __tablename__ = 'report_waihu'

    id = Column(db.Integer, primary_key=True)
    date = Column(db.Date, nullable=False)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#操作员
    operator = db.relationship('Operator', primaryjoin="(Waihu.operator_id == Operator.id)")
    usercount = Column(db.Integer, default=0, nullable=False)#用户量
    cjusercount = Column(db.Integer, default=0, nullable=False)#成交用户量
    usercount1 = Column(db.Integer, default=0, nullable=False)#1月内用户量
    usercount3 = Column(db.Integer, default=0, nullable=False)#1-3月用户量
    usercount6 = Column(db.Integer, default=0, nullable=False)#3-6月用户量
    usercount12 = Column(db.Integer, default=0, nullable=False)#6-12月用户量
    usercount1n = Column(db.Integer, default=0, nullable=False)#一年以上用户量
    jxusercount1 = Column(db.Integer, default=0, nullable=False)#1月内用户量接线
    jxusercount3 = Column(db.Integer, default=0, nullable=False)#1-3月用户量
    jxusercount6 = Column(db.Integer, default=0, nullable=False)#3-6月用户量
    jxusercount12 = Column(db.Integer, default=0, nullable=False)#6-12月用户量
    jxusercount1n = Column(db.Integer, default=0, nullable=False)#一年以上用户量
    tqusercount1 = Column(db.Integer, default=0, nullable=False)#1月内用户量TQ
    tqusercount3 = Column(db.Integer, default=0, nullable=False)#1-3月用户量
    tqusercount6 = Column(db.Integer, default=0, nullable=False)#3-6月用户量
    tqusercount12 = Column(db.Integer, default=0, nullable=False)#6-12月用户量
    tqusercount1n = Column(db.Integer, default=0, nullable=False)#一年以上用户量
    qtusercount1 = Column(db.Integer, default=0, nullable=False)#1月内用户量其他
    qtusercount3 = Column(db.Integer, default=0, nullable=False)#1-3月用户量
    qtusercount6 = Column(db.Integer, default=0, nullable=False)#3-6月用户量
    qtusercount12 = Column(db.Integer, default=0, nullable=False)#6-12月用户量
    qtusercount1n = Column(db.Integer, default=0, nullable=False)#一年以上用户量
    
    jxusercount = Column(db.Integer, default=0, nullable=False)#用户量接线
    tqusercount = Column(db.Integer, default=0, nullable=False)#用户量tq
#成交
    jxcjusercount = Column(db.Integer, default=0, nullable=False)#用户量接线
    tqcjusercount = Column(db.Integer, default=0, nullable=False)#用户量tq

    jxcjusercount1 = Column(db.Integer, default=0, nullable=False)#1月内用户量接线
    jxcjusercount3 = Column(db.Integer, default=0, nullable=False)#1-3月用户量
    jxcjusercount6 = Column(db.Integer, default=0, nullable=False)#3-6月用户量
    jxcjusercount12 = Column(db.Integer, default=0, nullable=False)#6-12月用户量
    jxcjusercount1n = Column(db.Integer, default=0, nullable=False)#一年以上用户量
    tqcjusercount1 = Column(db.Integer, default=0, nullable=False)#1月内用户量TQ
    tqcjusercount3 = Column(db.Integer, default=0, nullable=False)#1-3月用户量
    tqcjusercount6 = Column(db.Integer, default=0, nullable=False)#3-6月用户量
    tqcjusercount12 = Column(db.Integer, default=0, nullable=False)#6-12月用户量
    tqcjusercount1n = Column(db.Integer, default=0, nullable=False)#一年以上用户量
    qtcjusercount1 = Column(db.Integer, default=0, nullable=False)#1月内用户量其他
    qtcjusercount3 = Column(db.Integer, default=0, nullable=False)#1-3月用户量
    qtcjusercount6 = Column(db.Integer, default=0, nullable=False)#3-6月用户量
    qtcjusercount12 = Column(db.Integer, default=0, nullable=False)#6-12月用户量
    qtcjusercount1n = Column(db.Integer, default=0, nullable=False)#一年以上用户量


    usersales = Column(db.Integer, default=0, nullable=False)#业绩
    jxusersales1 = Column(db.Integer, default=0, nullable=False)#1月内业绩接线
    jxusersales3 = Column(db.Integer, default=0, nullable=False)#1-3月业绩
    jxusersales6 = Column(db.Integer, default=0, nullable=False)#3-6月业绩
    jxusersales12 = Column(db.Integer, default=0, nullable=False)#6-12月业绩
    jxusersales1n = Column(db.Integer, default=0, nullable=False)#一年以上业绩
    tqusersales1 = Column(db.Integer, default=0, nullable=False)#1月内业绩TQ
    tqusersales3 = Column(db.Integer, default=0, nullable=False)#1-3月业绩
    tqusersales6 = Column(db.Integer, default=0, nullable=False)#3-6月业绩
    tqusersales12 = Column(db.Integer, default=0, nullable=False)#6-12月业绩
    tqusersales1n = Column(db.Integer, default=0, nullable=False)#一年以上业绩
    qtusersales1 = Column(db.Integer, default=0, nullable=False)#1月内业绩其他
    qtusersales3 = Column(db.Integer, default=0, nullable=False)#1-3月业绩
    qtusersales6 = Column(db.Integer, default=0, nullable=False)#3-6月业绩
    qtusersales12 = Column(db.Integer, default=0, nullable=False)#6-12月业绩
    qtusersales1n = Column(db.Integer, default=0, nullable=False)#一年以上业绩

    ordercount = Column(db.Integer, default=0, nullable=False)#订单数
    jxordercount1 = Column(db.Integer, default=0, nullable=False)#1月内订单数接线
    jxordercount3 = Column(db.Integer, default=0, nullable=False)#1-3月订单数
    jxordercount6 = Column(db.Integer, default=0, nullable=False)#3-6月订单数
    jxordercount12 = Column(db.Integer, default=0, nullable=False)#6-12月订单数
    jxordercount1n = Column(db.Integer, default=0, nullable=False)#一年以上订单数
    tqordercount1 = Column(db.Integer, default=0, nullable=False)#1月内订单数TQ
    tqordercount3 = Column(db.Integer, default=0, nullable=False)#1-3月订单数
    tqordercount6 = Column(db.Integer, default=0, nullable=False)#3-6月订单数
    tqordercount12 = Column(db.Integer, default=0, nullable=False)#6-12月订单数
    tqordercount1n = Column(db.Integer, default=0, nullable=False)#一年以上订单数
    qtordercount1 = Column(db.Integer, default=0, nullable=False)#1月内订单数其他
    qtordercount3 = Column(db.Integer, default=0, nullable=False)#1-3月订单数
    qtordercount6 = Column(db.Integer, default=0, nullable=False)#3-6月订单数
    qtordercount12 = Column(db.Integer, default=0, nullable=False)#6-12月订单数
    qtordercount1n = Column(db.Integer, default=0, nullable=False)#一年以上订单数

    qsusersales = Column(db.Integer, default=0, nullable=False)#签收业绩
    qsorders = Column(db.Integer, default=0, nullable=False)#签收订单数

    last_jxusercount = Column(db.Integer, default=0, nullable=False)#用户量接线
    last_tqusercount = Column(db.Integer, default=0, nullable=False)#用户量tq
#成交
    last_jxcjusercount = Column(db.Integer, default=0, nullable=False)#用户量接线
    last_tqcjusercount = Column(db.Integer, default=0, nullable=False)#用户量tq

    last_usercount = Column(db.Integer, default=0, nullable=False)#上月用户量
    last_cjusercount = Column(db.Integer, default=0, nullable=False)#上月成交用户量
    last_usersales = Column(db.Integer, default=0, nullable=False)#上月业绩
    callusers = Column(db.Integer, default=0, nullable=False)#拨打数据
    nocallusers = Column(db.Integer, default=0, nullable=False)#未拨打数据
    silenceusers = Column(db.Integer, default=0, nullable=False)#沉默用户量
    newusers = Column(db.Integer, default=0, nullable=False)#新进用户量
    giveupusers = Column(db.Integer, default=0, nullable=False)#放弃用户量
    ordercount = Column(db.Integer, default=0, nullable=False)#订单数
    tuihuoorders = Column(db.Integer, default=0, nullable=False)#退货订单数
    tuihuosales = Column(db.Integer, default=0, nullable=False)#退货总额

class Jiexian(db.Model):
    '''接线'''
    __tablename__ = 'report_jiexian'

    id = Column(db.Integer, primary_key=True)
    date = Column(db.Date, nullable=False)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#操作员
    operator = db.relationship('Operator', primaryjoin="(Jiexian.operator_id == Operator.id)")
    usercount = Column(db.Integer, default=0, nullable=False)#用户量
    cjusercount = Column(db.Integer, default=0, nullable=False)#成交用户量
    usersales = Column(db.Integer, default=0, nullable=False)#业绩
    last_usercount = Column(db.Integer, default=0, nullable=False)#上月用户量
    last_usersales = Column(db.Integer, default=0, nullable=False)#上月业绩
    last_cjusercount = Column(db.Integer, default=0, nullable=False)#成交用户量    
    ordercount = Column(db.Integer, default=0, nullable=False)#订单数
    jxusersales = Column(db.Integer, default=0, nullable=False)#接线业绩
    jxordercount = Column(db.Integer, default=0, nullable=False)#接线订单数
    wfusersales = Column(db.Integer, default=0, nullable=False)#外呼业绩
    wfordercount = Column(db.Integer, default=0, nullable=False)#外呼订单数


class Fuwu(db.Model):
    '''服务'''
    __tablename__ = 'report_fuwu'

    id = Column(db.Integer, primary_key=True)
    date = Column(db.Date, nullable=False)
    operator_id = Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)#操作员
    operator = db.relationship('Operator', primaryjoin="(Fuwu.operator_id == Operator.id)")
    usercount = Column(db.Integer, default=0, nullable=False)#用户量
    usersales = Column(db.Integer, default=0, nullable=False)#业绩
    last_usercount = Column(db.Integer, default=0, nullable=False)#上月用户量
    last_usersales = Column(db.Integer, default=0, nullable=False)#上月业绩
    callusers = Column(db.Integer, default=0, nullable=False)#拨打数据
    nocallusers = Column(db.Integer, default=0, nullable=False)#未拨打数据
    silenceusers = Column(db.Integer, default=0, nullable=False)#沉默用户量
    isableeusers = Column(db.Integer, default=0, nullable=False)#停用用户量
    newusers = Column(db.Integer, default=0, nullable=False)#新进用户量
    giveupusers = Column(db.Integer, default=0, nullable=False)#放弃用户量
    fugouusercount = Column(db.Integer, default=0, nullable=False)#复购用户量
    fugousales = Column(db.Integer, default=0, nullable=False)#复购总额

class Fuwu2(db.Model):
    '''服务2'''
    __tablename__ = 'report_fuwu2'

    id = Column(db.Integer, primary_key=True)
    date = Column(db.Date, nullable=False)
    area = Column(db.String(150))#区域
    usercount = Column(db.Integer, default=0, nullable=False)#用户量
    youxiao = Column(db.Integer, default=0, nullable=False)#
    wuxiao = Column(db.Integer, default=0, nullable=False)#
    usersum = Column(db.Integer, default=0, nullable=False)#
