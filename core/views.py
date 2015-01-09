# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime
from collections import defaultdict,OrderedDict
from collections import namedtuple
from functools import partial

from flask import current_app,send_from_directory, session, jsonify, Blueprint, render_template, flash, request, redirect, url_for, json, abort
from flask.ext.login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc,asc,func
from sqlalchemy.orm import defer
from flask.ext.sqlalchemy import Pagination
from utils.tools import printException,des
import pycurl
from StringIO import StringIO
from global_settings import DMURL,DMD_ID

from extensions import db
from .forms import KnowledgeForm,CategoryForm, LoginForm, UserForm, NewsForm, OperatorForm, ItemForm, SkuForm, StockInForm,StockOutForm,LossForm, PasswordForm
from .models import User_tjfg,User_Isable,QXHKHDJ,Security_Codekh,QXHDM_Orderyf,Order_Operator,Outbound,Knowledge,Knowledge_Category,User_Voucher,User_Statistics,Order_LHYD_Postal,Security_Code,Security_Code_Log,User_Giveup,User_Assign_Log,SMS,Operator, Role, Item, Sku,Sku_Stock,Stock_Out, Stock_In, Sku_Set,Loss, Stock, IO_Log, Order, Order_Sets, Order_Log, User, User_Dialog, User_Phone, Address, Order_Item, News#Permission,Role,
from settings.constants import *
from utils.memcached import cache
from utils.decorator import admin_required,cached,view_cached
import suds
from xml.dom import minidom
admin = Blueprint('admin', __name__)


# def check_perm(action_name):
#     if current_user.is_admin or Permission(ActionNeed(action_name)):
#         return True
#     return False

# OrderNeed = namedtuple('OrderNeed', ['method', 'value'])
# OrderManageNeed = partial(OrderNeed, 'manage')
#
# class OrderMangePermission(Permission):
#     def __init__(self, status):
#         need = OrderManageNeed(unicode(status))
#         super(OrderMangePermission, self).__init__(need)


def _pending_order_nums():
    '''获取待处理订单数'''
    if not current_user.is_admin:
        #增加库房的选择物流
        if current_user.role_id in KF_ROOLEIDS:
            return db.session.query(func.count(Order.order_id)).filter(db.and_(Order.assign_operator_id == current_user.id,
                                                                           Order.status<100,Order.store_id == current_user.store_id)).scalar()
        else:
            return db.session.query(func.count(Order.order_id)).filter(db.and_(Order.assign_operator_id == current_user.id,
                                                                           Order.status<100)).scalar()
    else:
        return 0


@admin.route('/pending_order_nums', methods=['POST'])
@login_required
def pending_order_nums():
    return jsonify(num=_pending_order_nums())


@admin.route('/staff_reminder', methods=['POST'])
@login_required
def staff_reminder():
    orders = db.session.query(func.count(Order.order_id)).filter(db.and_(Order.assign_operator_id == current_user.id,Order.status<100)).scalar()
    #增加库房的选择物流
    if current_user.role_id in KF_ROOLEIDS:
        orders = db.session.query(func.count(Order.order_id)).filter(db.and_(Order.assign_operator_id == current_user.id,Order.status<100,Order.store_id == current_user.store_id)).scalar()    
    if current_user.role_id==ORDER_ROLE_ID:
        users = db.session.query(func.count(User.user_id)).filter(db.and_(User.assign_operator_id == current_user.id,
                                                                              User.expect_time!= None,
                                                                              User.expect_time<='%s 23:59:59'%(datetime.now().strftime('%Y-%m-%d')))).scalar()
    else:
        users = 0
    return jsonify(orders=orders,users=users)


@admin.route('/')
@login_required
def index():
    news_list = News.query.order_by(desc(News.created)).limit(5)
    expect_user_nums = 0
    if current_user.assign_user_type>0:
        expect_user_nums = db.session.query(func.count(User.user_id)).filter(db.and_(User.assign_operator_id == current_user.id,
                                                                                User.expect_time!= None,
                                                                                User.expect_time<='%s 23:59:59'%(datetime.now().strftime('%Y-%m-%d')))).scalar()
    return render_template('index.html', news_list=news_list, order_nums=_pending_order_nums(),expect_user_nums=expect_user_nums)

@admin.route('/express/query')
def express():
    return render_template('express.html')


@admin.route('/change_op_status', methods=['POST'])
@login_required
def change_op_status():
    if current_user.status not in (1, 2,): return jsonify(result=False, error=u'当前状态不正常')
    to_status = 1 if current_user.status == 2 else 2
    current_user.status = to_status
    db.session.commit()
    current_app.logger.info('CHANGE_OPERATOR_STATUS|%s|%s' % (current_user.id, to_status))
    if to_status == 2: logout_user()
    return jsonify(result=True)


@admin.route('/news/manage')
@admin_required
def manage_news():
    page = int(request.args.get('page', 1))
    pagination = News.query.order_by(desc(News.created)).paginate(page, per_page=20)
    return render_template('admin/news.html', pagination=pagination)


@admin.route('/news/edit/<int:news_id>', methods=['POST', 'GET'])
@admin_required
def edit_news(news_id):
    news = News.query.get_or_404(news_id)
    form = NewsForm(obj=news)
    if form.validate_on_submit():
        form.populate_obj(news)
        db.session.commit()
        return redirect(url_for('admin.manage_news'))
    return render_template('admin/news_form.html', form=form, is_edit=True)


@admin.route('/news/add', methods=['GET', 'POST'])
@admin_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        news = News()
        form.populate_obj(news)
        db.session.add(news)
        db.session.commit()
        return redirect(url_for('admin.manage_news'))
    return render_template('admin/news_form.html', form=form)


@admin.route('/news/delete/<int:id>', methods=['POST'])
@admin_required
def del_news(id):
    try:
        news = News.query.get(id)
    except:
        return jsonify(result=False, error=u'公告不存在')
    db.session.delete(news)
    db.session.commit()
    return jsonify(result=True)


@admin.route('/api/users.json')
@login_required
def simple_users():
    q = request.args.get('q', None)
    result = []
    if q:
        _conditions = [db.or_(User.name.like('%' + q + '%'), User.phone.like('%' + q + '%'))]
        if not current_user.is_admin:
            _conditions.append(User.assign_operator_id==current_user.id)
        users = User.query.filter(*_conditions)
        for u in users:
            result.append({'user_id': u.user_id, 'name': u.name, 'tel': u.phone})
    return jsonify(users=result)


@admin.route('/api/address/<int:user_id>')
@login_required
def user_address_api(user_id):
    _addresses = []
    addresses = Address.query.filter(Address.user_id == user_id).order_by(desc(Address.id))
    for addr in addresses:
        _addresses.append({'id': addr.id,
                           'ship_to': addr.ship_to,
                           'tel': addr.tel,
                           'phone': addr.phone,
                           'province': addr.province,
                           'city': addr.city,
                           'district': addr.district,
                           'street1': addr.street1,
                           'street2': addr.street2,
                           'email': addr.email,
                           'format_address': addr.format_address,
                           'postcode': addr.postcode,
                           'is_default':addr.is_default})

    return jsonify(addresses=_addresses)


@admin.route('/address/update/<int:address_id>/<int:user_id>', methods=['POST', 'GET'])
@admin_required
def update_address(address_id,user_id):
    if request.method == 'POST':
        if address_id:#更新地址
            address = Address.query.filter(Address.id == address_id).first()
            if not address: return jsonify(result=False, error=u"地址不存在")
            if address.user_id<>user_id:return jsonify(result=False,error="非法操作！")
        else:
            address = Address()
            address.user_id = user_id

        try:
            address.ship_to = request.form['ship_to']
            address.province = request.form['province']
            address.city = request.form['city']
            address.district = request.form['district']
            address.street1 = request.form['street1']
            address.phone = request.form['phone']
            address.tel = request.form['tel']
            address.email = request.form['email']
            address.postcode = request.form['postcode']
            if not address_id:db.session.add(address)
            db.session.commit()
            return jsonify(result=True, error='')
        except Exception, e:
            current_app.logger.error('update address(%d) failed, error: %s.' % (address_id, e))
            return jsonify(result=False, error=e.message)

    if not address_id: abort(404)
    address = Address.query.get_or_404(address_id)
    return render_template('user/update_address.html', address=address)


@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(request.args.get('next', None) or url_for('admin.index'))
    form = LoginForm(next=request.args.get('next', None))
    if form.validate_on_submit():
        operator, authenticated = Operator.authenticate(form.username.data, form.password.data)
        if operator and authenticated:
            if login_user(operator):#, remember='y'
                #identity_changed.send(current_app._get_current_object(), identity=Identity(operator.id))
                return redirect(form.next.data or url_for('admin.index'))
        current_app.logger.debug('login(api) failed, username: %s.' % form.username.data)
        flash('用户名或密码错误', 'error')
    return render_template('admin/login.html', form=form)


@admin.route('/operator/change_password', methods=['GET', 'POST'])
@login_required
def password():
    form = PasswordForm(next=request.args.get('next'))
    if form.validate_on_submit():
        operator = Operator.query.filter_by(username=current_user.username).first_or_404()
        operator.password = form.new_password.data
        db.session.commit()

        flash('密码已修改.', 'success')
    return render_template('admin/password.html', form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    # # Remove session keys set by Flask-Principal
    # for key in ('identity','identity.name', 'identity.auth_type'):
    #     session.pop(key, None)
    #
    # # Tell Flask-Principal the user is anonymous
    # identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(url_for('admin.login'))


@admin.route('/operator/edit/<int:operator_id>', methods=['GET', 'POST'])
@admin_required
def edit_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)
    form = OperatorForm(obj=operator)
    form.username(readonly=True)
    if form.validate_on_submit():
        operator.nickname = form.nickname.data
        operator.email = form.email.data
        operator.username = form.username.data
        operator.op_id = form.op_id.data
        operator.store_id = form.store_id.data
        operator.assign_user_type = form.assign_user_type.data
        operator.team = form.team.data if form.team.data else None
        if form.password.data and len(form.password.data) >= 6:
            operator.password = form.password.data
        operator.role_id = int(form.role.data.id)
        operator.is_admin = form.is_admin.data
        db.session.commit()
        flash(u'帐号修改成功！')
        return redirect(url_for('admin.operators'))
    return render_template('admin/operator_form.html', form=form, is_edit=True)


@admin.route('/operator/add', methods=['GET', 'POST'])
@admin_required
def add_operator():
    form = OperatorForm(next=request.args.get('next'))
    if form.validate_on_submit():
        operator = Operator()
        operator.nickname = form.nickname.data
        operator.email = form.email.data
        operator.username = form.username.data
        operator.op_id = form.op_id.data
        operator.store_id = form.store_id.data
        operator.password = form.password.data
        operator.team = form.team.data if form.team.data else None
        operator.role_id = int(form.role.data.id)
        operator.status = 2
        operator.assign_user_type = form.assign_user_type.data
        operator.is_admin = form.is_admin.data
        db.session.add(operator)
        db.session.commit()
        flash(u'帐号创建成功！')
        return redirect(url_for('admin.operators'))
    return render_template('admin/operator_form.html', form=form)


@admin.route('/operator/list', methods=['GET', 'POST'])
@admin_required
def operators():
    q = request.args.get('q', None)
    page = int(request.args.get('page', 1))
    PER_PAGE = 20
    if q:
        pagination = Operator.query.join(Role,Operator.role_id==Role.id).filter(db.or_(Operator.nickname.like('%%%s%%' % q),
                                                  Operator.username.like('%%%s%%' % q))).paginate(page,
                                                                                                  per_page=PER_PAGE)
    else:
        pagination = Operator.query.paginate(page, per_page=PER_PAGE)
    return render_template('admin/operators.html', pagination=pagination)


@admin.route('/operator/delete/<int:id>', methods=['POST'])
@admin_required
def del_operator(id):
    try:
        operator = Operator.query.get(id)
    except:
        return jsonify(result=False, error=u'帐号不存在')
    if operator.id == current_user.id:
        return jsonify(result=False, error=u'无法删除自己')
    #db.session.delete(operator)
    operator.status = 9
    db.session.commit()
    return jsonify(result=True)


@admin.route('/operator/role/list')
@admin_required
def roles():
    roles = Role.query.all()
    _roles = []
    for role in roles:
        _endpoints = {}
        for _endpoint,name,_module in ENDPOINTS:
            if _endpoint in role.endpoints:
                if not _endpoints.has_key(_module):
                    _endpoints[_module] = {'module_name':MODULES[_module],'endpoints':[]}
                _endpoints[_module]['endpoints'].append(name)
        _roles.append((role.id,role.name,_endpoints))
    return render_template('admin/roles.html',roles=_roles)


@admin.route('/operator/role/manage', methods=['GET', 'POST'])
@admin_required
def manage_role():
    if request.method == 'POST':
        _endpoints = json.loads(request.form['endpoints'])
        _role_name = request.form['name']
        role_id = int(request.form['role_id'])
        if not role_id:
            role = Role()
            role.name = _role_name
            role.endpoints = _endpoints
            db.session.add(role)
            db.session.commit()
            return jsonify(result=True)
        else:
            try:
                role = Role.query.get(role_id)
            except:
                return jsonify(result=False,error=u'编辑角色不存在')
            role.name = _role_name
            role.endpoints = _endpoints
            db.session.commit()
            return jsonify(result=True)

    role_id = request.args.get('role_id',0)
    if role_id:
        role = Role.query.get(role_id)
    else:
        role = None
    perms = defaultdict(list)
    for endpoint,name,module_id in ENDPOINTS:
        perms[module_id].append((endpoint,name))
    return render_template('admin/role_form.html',perms=perms,role=role)


# @admin.route('/operator/permission/manage', methods=['GET', 'POST'])
# def permissions():
#     if request.method == 'POST':
#         endpoint = request.form.get('endpoint', None)
#         uri = request.form.get('uri', None)
#         if endpoint and uri:
#             if Permission.query.filter_by(uri=uri).first() is not None:
#                 flash(u'该权限已配置', category='error')
#             else:
#                 perm = Permission()
#                 perm.endpoint = endpoint
#                 perm.uri = uri
#                 db.session.add(perm)
#                 db.session.commit()
#                 flash(u'权限已添加')
#
#     page = int(request.args.get('page', 1))
#     pagination = Permission.query.order_by(Permission.id.desc()).paginate(page, per_page=50)
#     return render_template('admin/permissions.html', pagination=pagination)
#
#
# @admin.route('/operator/permission/delete/<int:id>')
# def del_perm(id):
#     perm = Permission.query.get_or_404(id)
#     db.session.delete(perm)
#     db.session.commit()
#     return redirect(url_for('admin.permissions'))
#

# @admin.route('/operator/role/manage', methods=['GET', 'POST'])
# @admin.route('/operator/role/manage/<int:role_id>', methods=['GET', 'POST'])
# def role(role_id=0):
#     _role = None
#     select_id = 0
#     if role_id:
#         _role = Role.query.filter(Role.id == role_id).first_or_404()
#         select_id = _role.id
#
#     form = RoleForm(obj=_role)
#     if form.validate_on_submit():
#         if not _role: _role = Role()
#         form.populate_obj(_role)
#         _role.name = form.name.data
#         _role.permissions = form.permissions.data
#         is_new = False
#         if not _role.id:
#             db.session.add(_role)
#             is_new = True
#         db.session.commit()
#         flash(u'角色创建成功' if is_new else u'角色修改成功')
#         return redirect(request.path)
#
#     roles = Role.query.all()
#     return render_template('admin/role.html', form=form, roles=roles, role_id=select_id)


############################################
@admin.route('/item/manage', methods=['POST', 'GET'])
@admin_required
def items():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item()
        form.populate_obj(item)
        db.session.add(item)
        db.session.commit()
        flash(u'商品《%s》已添加！' % form.name.data)
        return redirect(request.path)
    items = Item.query.filter(Item.status == True)
    return render_template('item/item.html', form=form, items=items)


@admin.route('/item/del/<int:item_id>', methods=['POST'])
@admin_required
def del_item(item_id):
    try:
        item = Item.query.get(item_id)
    except:
        return jsonify(result=False, error=u'商品不存在')

    item.status = False
    db.session.commit()
    return jsonify(result=True)


@admin.route('/item/sku/list', methods=['POST', 'GET'])
@admin_required
def skus():
    q = request.args.get('q', None)
    page = int(request.args.get('page', 1))
    PER_PAGE = 20
    if q:
        pagination = Sku.query.filter(db.or_(Sku.name.like('%%%s%%' % q),
                                             Sku.id == q)).order_by(Sku.quantity_flag).paginate(page, per_page=PER_PAGE)
    else:
        pagination = Sku.query.order_by(Sku.quantity_flag).paginate(page, per_page=PER_PAGE)
    return render_template('item/skus.html', pagination=pagination)


@admin.route('/item/sku/edit/<int:sku_id>', methods=['POST', 'GET'])
@admin_required
def edit_sku(sku_id):
    sku = Sku.query.get_or_404(sku_id)
    form = SkuForm(obj=sku, **sku.properties)
    if form.validate_on_submit():
        #更新各仓库商品阀值
        if sku.threshold <> form.threshold.data:
            Sku_Stock.query.filter(Sku_Stock.sku_id==sku.id).update({'threshold':form.threshold.data})
        form.populate_obj(sku)
        properties = {}
        for p in SKU_PROPERTIES:
            if hasattr(form, p):
                _data = getattr(form, p).data
                if _data: properties[p] = _data
        if properties:
            sku.properties = ','.join(['%s:u"%s"' % (k, v) for k, v in properties.iteritems()])
        db.session.commit()
        cache.delete(ALLOWED_ORDER_ITEMS_CACHE_KEY)
        return redirect(url_for('admin.skus'))
    return render_template('item/sku_form.html', form=form, is_edit=True)


@admin.route('/item/sku/add', methods=['POST', 'GET'])
@admin_required
def add_sku():
    form = SkuForm()
    if form.validate_on_submit():
        sku = Sku()
        sku.name = form.name.data
        sku.item_id = form.item.data.id
        sku.code = form.code.data
        properties = {}
        for p in SKU_PROPERTIES:
            if hasattr(form, p):
                _data = getattr(form, p).data
                if _data: properties[p] = _data
        if properties:
            sku.properties = ','.join(['%s:u"%s"' % (k, v) for k, v in properties.iteritems()])
        sku.price = form.price.data
        sku.unit = form.unit.data
        sku.threshold = form.threshold.data
        sku.warning_threshold = form.warning_threshold.data
        sku.market_price = form.market_price.data
        sku.discount_price = form.discount_price.data
        sku.allowed_gift = form.allowed_gift.data
        sku.status = form.status.data
        db.session.add(sku)
        db.session.flush()
        sku.init_stocks()#初始化商品库房库存
        db.session.commit()
        flash(u'添加商品SKU成功')
        cache.delete(ALLOWED_ORDER_ITEMS_CACHE_KEY)
        return redirect(url_for('admin.skus'))
    return render_template('item/sku_form.html', form=form)



@admin.route('/item/sku_set/add',methods=['GET','POST'])
@admin_required
def add_sku_set():
    if request.method=='POST':
        try:
            name = request.form['name']
            items = json.loads(request.form['items'])#商品
            price = float(request.form['price'])

            sku_set = Sku_Set()
            sku_set.name = name
            sku_set.config = dict([(int(k), int(d['quantity'])) for k, d in items.iteritems()])
            sku_set.price_config = dict([(int(k), float(d['discount_price'])) for k, d in items.iteritems()])
            sku_set.price = price
            db.session.add(sku_set)
            db.session.commit()
            cache.delete(ALLOWED_ORDER_ITEMS_CACHE_KEY)
            return jsonify(result=True)
        except Exception, e:
            db.session.rollback()
            current_app.logger.error('add sku set failed, error: %s.' % e)
            return jsonify(result=False, error=e)

    items = Sku.query.all()
    return render_template('item/add_sku_set.html', items=items)


@admin.route('/item/sku_set/update_status/<int:sku_set_id>',methods=['POST'])
def update_sku_set_status(sku_set_id):
    try:
        sku_set = Sku_Set.query.get(sku_set_id)
    except:
        return jsonify(result=False,error=u'套餐不存在')
    sku_set.is_valid = (not sku_set.is_valid)
    db.session.commit()
    cache.delete(ALLOWED_ORDER_ITEMS_CACHE_KEY)
    return jsonify(result=True)

@admin.route('/item/sku_set/manage')
@admin_required
def sku_set_manage():
    page = int(request.args.get('page', 1))
    pagination = Sku_Set.query.paginate(page, per_page=20)
    return render_template('item/sku_sets.html', pagination=pagination)


@admin.route('/stock/edit/<int:stock_id>', methods=['POST', 'GET'])
@admin_required
def edit_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    if stock.status not in (1,2,): abort(404)
    form = StockForm(obj=stock)
    if form.validate_on_submit():
        form.populate_obj(stock)
        if stock.status==1:
            stock.status = 2
        stock.operator_id = current_user.id
        db.session.commit()
        return redirect(url_for('admin.stocks'))
    return render_template('stock/stock_form.html', form=form, is_edit=True)


@admin.route('/stock/list')
@admin_required
def stocks():
    q = request.args.get('q', None)
    page = int(request.args.get('page', 1))
    PER_PAGE = 20
    if q:
        pagination = Stock.query.join(Sku,Sku.id==Stock.sku_id).filter(db.or_(Stock.sku_id == q,
                                                                              Sku.name.like('%' + q + '%'))).order_by(desc(Stock.created)).paginate(page,per_page=PER_PAGE)
    else:
        pagination = Stock.query.order_by(desc(Stock.created)).paginate(page, per_page=PER_PAGE)
    return render_template('stock/stocks.html', pagination=pagination)


@admin.route('/stock/approval/<int:stock_id>', methods=['POST'])
@admin_required
def stock_approval(stock_id):
    try:
        stock = Stock.query.get(stock_id)
    except:
        return jsonify(result=False, error=u'库存信息不存在.')

    if stock.status <> 2: return jsonify(result=False, error=u'非法操作')

    is_confirm = int(request.form['confirm'])
    if is_confirm:
        stock.status = 9
        _sku = stock.sku
        _sku.quantity = Sku.quantity + stock.in_quantity
        IO_Log.add(_sku.id, stock.id, 10, stock.in_quantity)#出入库日志
    else:
        stock.status = 1
    db.session.commit()
    return jsonify(result=True)


@admin.route('/stock/in/list')
@admin_required
def stock_in_list():
    q = request.args.get('q', None)
    page = int(request.args.get('page', 1))
    PER_PAGE = 20
    _conditions = []

    name = request.args.get('name', None)
    if name: _conditions.append(Sku.name.like('%' + name + '%'))

    sku_id = request.args.get('sku_id', None)
    if sku_id: _conditions.append(Stock_In.sku_id==sku_id)

    store_id = request.args.get('store_id', 0)
    if store_id: _conditions.append(Stock_In.store_id == int(store_id))

    c = request.args.get('c', 0)
    if c: _conditions.append(Stock_In.c == int(c))

    status = request.args.get('status', 0)
    if status: _conditions.append(Stock_In.status == int(status))

    _start_date = request.args.get('start_date','')
    if _start_date:
        _conditions.append(Stock_In.created>=_start_date)

    _end_date = request.args.get('end_date','')
    if _end_date:
        _conditions.append(Stock_In.created<=_start_date)
    
    if len(_conditions)>0:
        pagination = Stock_In.query.join(Sku,Sku.id==Stock_In.sku_id).filter(*_conditions).order_by(desc(Stock_In.created)).paginate(page, per_page=PER_PAGE)
    else:
        pagination = Stock_In.query.join(Sku,Sku.id==Stock_In.sku_id).order_by(asc(Stock_In.status),desc(Stock_In.created)).paginate(page, per_page=PER_PAGE)
    return render_template('stock/stock_in_list.html', pagination=pagination)


@admin.route('/stock/in/approval', methods=['POST'])
@admin_required
def stock_in_approval():
    '''入库审批'''
    stock_id = request.form['stock_id']
    stock_in = Stock_In.query.get(stock_id)
    if not stock_in:
        return jsonify(result=False, error=u'入库记录不存在.')
    if stock_in.status <> 2: return jsonify(result=False, error=u'非法操作')
    is_confirm = int(request.form['confirm'])
    if is_confirm:
        sku_stock = stock_in.sku_stock
        if not sku_stock:
            return jsonify(result=False,error=u'该商品库存记录不存在!')
        stock_in.valid_time = datetime.now()
        stock_in.status = 9
        sku_stock.quantity = Sku_Stock.quantity + stock_in.quantity
    else:
        stock_in.status = 1
    stock_in.approver_id = current_user.id
    stock_in.approval_time = datetime.now()
    db.session.commit()
    return jsonify(result=True)

@admin.route('/stock/in/add', methods=['POST', 'GET'])
@admin_required
def add_stock_in():
    form = StockInForm()
    if form.validate_on_submit():
        try:
            stock_in = Stock_In()
            _sku = form.sku.data
            _in_quantity = form.quantity.data
            if _in_quantity <= 0:
                raise Exception(u'入库数量错误')
            print (int(form.store_id.data) != int(current_user.store_id))
            print (form.store_id.data)
            print (current_user.store_id)
            #增加库房的选择物流
            if current_user.role_id in KF_ROOLEIDS and int(form.store_id.data) != int(current_user.store_id):
                raise Exception(u'仓库选择错误')
            stock_in.sku_id = _sku.id
            stock_in.store_id = form.store_id.data
            stock_in.c = form.c.data
            stock_in.shelf_number = form.shelf_number.data
            stock_in.code = form.code.data
            stock_in.made_in = form.made_in.data
            stock_in.mfg_date = form.mfg_date.data
            stock_in.exp_date = form.exp_date.data
            stock_in.quantity = _in_quantity
            stock_in.purchase_price = form.purchase_price.data
            stock_in.status = 2
            stock_in.operator_id = current_user.id
            stock_in.remark = form.remark.data
            db.session.add(stock_in)
            db.session.commit()
            current_app.logger.info('STOCK|IN|%s|%s|%s|%s', _sku.id, stock_in.shelf_number, stock_in.code, _in_quantity,
                                    current_user.id)
            flash(u'入库登记成功,等待财务审核中！')
            return redirect(url_for('admin.stock_in_list'))
        except Exception, e:
            current_app.logger.error('add stock in failed, error: %s.' % e)
            db.session.rollback()
            #flash(u'登记入库发生错误！', 'error')
            flash(e.message, 'error')
    return render_template('stock/stock_in_form.html', form=form, is_edit=False)


@admin.route('/stock/in/edit/<int:stock_id>', methods=['POST', 'GET'])
@admin_required
def edit_stock_in(stock_id):
    stock_in = Stock_In.query.get_or_404(stock_id)
    if stock_in.status not in (1,2,): abort(404)
    form = StockInForm(obj=stock_in)
    if form.validate_on_submit():
        form.populate_obj(stock_in)
        if not form.order_id.data:stock_in.order_id = None
        if stock_in.status==1:
            stock_in.status = 2
        stock_in.operator_id = current_user.id
        db.session.commit()
        return redirect(url_for('admin.stock_in_list'))
    return render_template('stock/stock_in_form.html', form=form, is_edit=True)

@admin.route('/stock/out/list')
@admin_required
def stock_out_list():
    q = request.args.get('q', None)
    page = int(request.args.get('page', 1))
    PER_PAGE = 20
    _conditions = []

    name = request.args.get('name', None)
    if name: _conditions.append(Sku.name.like('%' + name + '%'))

    sku_id = request.args.get('sku_id', None)
    if sku_id: _conditions.append(Stock_Out.sku_id==sku_id)

    store_id = request.args.get('store_id', 0)
    if store_id: _conditions.append(Stock_Out.store_id == int(store_id))

    c = request.args.get('c', 0)
    if c: _conditions.append(Stock_Out.c == int(c))

    status = request.args.get('status', 0)
    if status: _conditions.append(Stock_Out.status == int(status))

    _start_date = request.args.get('start_date','')
    if _start_date:
        _conditions.append(Stock_Out.created>='%s 00:00:00'%_start_date)

    _end_date = request.args.get('end_date','')
    if _end_date:
        _conditions.append(Stock_Out.created<='%s 23:59:59'%_end_date)

    if len(_conditions)>0:
        pagination = Stock_Out.query.join(Sku,Sku.id==Stock_Out.sku_id).filter(*_conditions).order_by(desc(Stock_Out.created)).paginate(page, per_page=PER_PAGE)
    else:
        pagination = Stock_Out.query.join(Sku,Sku.id==Stock_Out.sku_id).order_by(asc(Stock_Out.status),desc(Stock_Out.created)).paginate(page, per_page=PER_PAGE)
    return render_template('stock/stock_out_list.html', pagination=pagination)


@admin.route('/stock/out/approval', methods=['POST'])
@admin_required
def stock_out_approval():
    '''出库审批'''
    stock_id = request.form['stock_id']
    stock_out = Stock_Out.query.get(stock_id)
    if not stock_out:
        return jsonify(result=False, error=u'出库记录不存在.')
    if stock_out.status <> 2: return jsonify(result=False, error=u'非法操作')
    is_confirm = int(request.form['confirm'])
    if is_confirm:
        sku_stock = stock_out.sku_stock
        if not sku_stock:return jsonify(result=False,error=u'该商品库存记录不存在!')
        if sku_stock.quantity<stock_out.quantity:
            return jsonify(result=False,error=u'商品库存不足，无法出库！')
        stock_out.valid_time = datetime.now()
        sku_stock.quantity = Sku_Stock.quantity - stock_out.quantity
        stock_out.status = 9
    else:
        stock_out.status = 1
    stock_out.approver_id = current_user.id
    stock_out.approval_time = datetime.now()
    db.session.commit()
    return jsonify(result=True)


@admin.route('/stock/out/add', methods=['POST', 'GET'])
@admin_required
def add_stock_out():
    form = StockOutForm()
    if form.validate_on_submit():
        try:
            stock_out = Stock_Out()
            _sku = form.sku.data
            _quantity = form.quantity.data
            if _quantity <= 0:
                raise Exception(u'出库数量错误')
            #增加库房的选择物流
            if current_user.role_id in KF_ROOLEIDS and int(form.store_id.data) != int(current_user.store_id):
                raise Exception(u'仓库选择错误')


            stock_out.sku_id = _sku.id
            stock_out.store_id = form.store_id.data

            sku_stock = stock_out.sku_stock
            if not sku_stock:
                raise Exception(u'该商品库存记录不存在!')
            if sku_stock.actual_quantity<_quantity:
                raise Exception(u'商品库存不足，无法添加登记出库！')

            stock_out.c = form.c.data
            stock_out.code = form.code.data
            stock_out.quantity = _quantity
            stock_out.status = 2
            stock_out.operator_id = current_user.id
            stock_out.remark = form.remark.data
            db.session.add(stock_out)
            db.session.commit()
            current_app.logger.info('STOCK|OUT|%s|%s|%s|%s',stock_out.id,_sku.id,stock_out.code, _quantity,
                                    current_user.id)
            flash(u'出库登记完成,等待审核中！')
            return redirect(url_for('admin.stock_out_list'))
        except Exception, e:
            current_app.logger.error('add stock out failed, error: %s.' % e)
            db.session.rollback()
            flash(e.message, 'error')
    return render_template('stock/stock_out_form.html', form=form, is_edit=False)


@admin.route('/stock/out/edit/<int:stock_id>', methods=['POST', 'GET'])
@admin_required
def edit_stock_out(stock_id):
    stock_out = Stock_Out.query.get_or_404(stock_id)
    if stock_out.status not in (1,2,): abort(404)
    form = StockOutForm(obj=stock_out)
    if form.validate_on_submit():
        form.populate_obj(stock_out)
        if not form.order_id.data:stock_out.order_id = None
        if stock_out.status==1:
            stock_out.status = 2
        stock_out.operator_id = current_user.id
        db.session.commit()
        return redirect(url_for('admin.stock_out_list'))
    return render_template('stock/stock_out_form.html', form=form, is_edit=True)

@admin.route('/stock/delete', methods=['POST'])
@admin_required
def stock_delete():
    t = request.form['type']
    stock_id = request.form['stock_id']
    if t == 'IN':
        stock = Stock_In.query.get(stock_id)
    elif t == 'OUT':
        stock = Stock_Out.query.get(stock_id)

    if stock.status != 1:
        return jsonify(result=False,error=u'当前状态不允许删除库存')

    db.session.delete(stock)
    db.session.commit()
    return jsonify(result=True)


@admin.route('/stock/losses/list', methods=['POST', 'GET'])
@admin_required
def losses():
    q = request.args.get('q', None)
    page = int(request.args.get('page', 1))
    PER_PAGE = 20

    _conditions = []
    sku_id = request.args.get('sku_id', 0)
    if sku_id: _conditions.append(Loss.sku_id == int(sku_id))

    name = request.args.get('name', None)
    if name: _conditions.append(Sku.name.like('%' + name + '%'))

    status = int(request.args.get('status', 0))
    if status: _conditions.append(Loss.status == status)

    _start_date = request.args.get('start_date','')
    if _start_date:
        _conditions.append(Loss.created>='%s 00:00:00'%_start_date)

    _end_date = request.args.get('end_date','')
    if _end_date:
        _conditions.append(Loss.created<='%s 23:59:59'%_end_date)

    if len(_conditions)>0:
        pagination = Loss.query.join(Sku,Sku.id==Loss.sku_id).filter(*_conditions).paginate(page, per_page=PER_PAGE)
    else:
        pagination = Loss.query.join(Sku,Sku.id==Loss.sku_id).paginate(page, per_page=PER_PAGE)
    return render_template('stock/losses.html', pagination=pagination)


@admin.route('/stock/loss/approval/<int:loss_id>', methods=['POST'])
@admin_required
def loss_approval(loss_id):
    try:
        loss = Loss.query.get(loss_id)
    except:
        return jsonify(result=False, error=u'记录不存在.')

    if loss.status <> 2: return jsonify(result=False, error=u'非法操作')

    is_confirm = int(request.form['confirm'])
    if is_confirm:
        loss.status = 9
        _sku = loss.sku
        _sku.loss_quantity = Sku.loss_quantity + loss.quantity
    else:
        loss.status = 1
    db.session.commit()
    return jsonify(result=True)

@admin.route('/stock/losses/add', methods=['POST', 'GET'])
@admin_required
def add_loss():
    form = LossForm(link_order_id=request.args.get('link_order_id',None))
    if form.validate_on_submit():
        loss = Loss()
        if form.link_order_id.data:
            if db.session.query(func.count(Order.order_id)).filter(Order.order_id==form.link_order_id.data).scalar()==0:
                flash('订单号码不存在', 'error')
                return render_template('stock/loss_form.html',form=form)
            loss.link_order_id = form.link_order_id.data
            loss.type = 1
        else:
            loss.type = 2

        loss.sku_id = form.sku.data.id
        loss.quantity = form.quantity.data
        loss.channel = form.channel.data
        loss.degree = form.degree.data
        loss.operator_id = current_user.id
        loss.remark = form.remark.data
        loss.status = 2
        db.session.add(loss)
        db.session.commit()
        flash(u'报损登记已提交，请等待审批！')
        return redirect(url_for('admin.losses'))
    return render_template('stock/loss_form.html',form=form)


def _add_order(operator, request):
    '''创建订单'''
        #订单操作日志
    user_id = request.form['user_id']
    if not user_id: user_id = 0
    user_id = int(user_id)
    username = request.form.get('username', None)
    if not user_id:
        return False, u'客户为空'

    try:
        user = User.query.get(user_id)
    except:
        db.session.rollback()
        return False, u'客户不存在'

    if (not current_user.is_admin) and user.assign_operator_id != current_user.id:
        return False, u'该客户当前不归属你，无法创建订单！'

    # if not user_id and db.session.query(func.count(User.user_id)).filter(User.phone==request.form['phone']).scalar()>0:
    #     return False, u'电话号码已存在！'

    #商品
    items = json.loads(request.form['items'])
    if len(items) == 0: return False, u'选择商品不可为空'
    is_xlj = False
    for item_id, data in items.iteritems():
        _id = int(data['sku-id'])
        if _id==XLJ_ID:
            is_xlj=True
            break
    total_item_fee = 0
    totalitemfee = 0
    _sku_objs = {}
    _sku_sets = []
    _order_items = []
    for item_id, data in items.iteritems():
        quantity = int(data['quantity'])
        if quantity <= 0: return False, u'商品数量不正确'
        _type = data['type']
        _price = float(data['price'])
        _name = data['name']
        _id = int(data['sku-id'])
        if _type == 1:
            if _sku_objs.has_key(_id):
                _sku = _sku_objs[_id]
            else:
                _sku = Sku.query.get(_id)
                _sku_objs[_sku.id] = _sku

            if _price not in _sku.allowed_prices:
                return False,u'商品《%s》不允许使用价格：%s!'%(_sku.name,_price)

            _fee = _price * quantity
            total_item_fee += _fee
            if DRUGS.find(data['sku-id']+',') == -1:
                totalitemfee += _fee
            _order_items.append((_sku.id,'',_name,_price,quantity,_fee,_sku.unit,_sku.code))
        else:
            _sku_set = Sku_Set.query.get(_id)
            if not _sku_set.is_valid: return False, u'套餐《%s》当前未启用！' % _sku_set.name
            _sku_price_config = _sku_set.price_config
            for sku_id, per_quantity in _sku_set.config.iteritems():
                if _sku_objs.has_key(sku_id):
                    _sku = _sku_objs[sku_id]
                else:
                    _sku = Sku.query.get(sku_id)
                    _sku_objs[_sku.id] = _sku
                _quantity = per_quantity*quantity
                item_price = _sku_set.price_config[_sku.id]
                _fee = item_price * _quantity
                _order_items.append((_sku.id,_sku_set.name,_sku.name,item_price,_quantity,_fee,_sku.unit,_sku.code))
            total_item_fee += _sku_set.price * quantity
            if DRUGS.find(data['sku-id']+',') == -1:
                totalitemfee += _sku_set.price * quantity

            _sku_sets.append((_sku_set, quantity))
        
    #代金卷
    #djj = int(request.form.get('djj', 0))
    djj = json.loads(request.form['djj2'])
    djjlen = len(djj)

    djjtotle = 20*djjlen
    isdjj = 0
    if djjtotle == 20:
        if totalitemfee<500:
            isdjj = 1
    elif djjtotle == 40:
        if totalitemfee<1000:
            isdjj = 1
    elif djjtotle == 60:
        if totalitemfee<1500:
            isdjj = 1
    elif djjtotle == 80:
        if totalitemfee<2000:
            isdjj = 1
    if isdjj:
        return False, '代金卷使用过多'
    if djjlen > 0:
        for djjm in djj:
            voucheruser = User_Voucher.query.get(djjm)
            if voucheruser.user_id<>user_id or voucheruser.order_id>0:return False, '不能使用该代金卷'
    #return False, '不能使用该代金卷2'
    try:
        if user_id:
            try:
                user = User.query.get(user_id)
            except:
                db.session.rollback()
                return False, u'客户不存在'
        else:
            user = User()
            user.name = username
            user.gender = request.form.get('gender', u'保密')
            user.origin = int(request.form.get('user_origin', 0))
            user.phone = request.form['phone']
            user.email = request.form.get('email', '')
            user.operator_id = operator.id
            db.session.add(user)
            db.session.flush()

        #地址
        address_id = int(request.form.get('address_id', 0))
        if not address_id:
            address = Address()
            address.user_id = user.user_id
            address.province = request.form.get('province', None)
            address.city = request.form.get('city', None)
            address.district = request.form.get('district', None)
            address.street1 = request.form.get('street1', None)
            address.postcode = request.form.get('postcode', None)
            address.ship_to = request.form.get('ship_to', None)
            address.phone = request.form.get('phone', None)
            address.tel = request.form.get('tel', None)
            address.email = request.form.get('email', '')
            db.session.add(address)
            db.session.flush()
        else:
            address = Address.query.get(address_id)

        #订单
        order = Order()
        order.is_xlj = is_xlj
        _date = datetime.now().strftime('%y%m%d')
        order.date = _date
        order.order_id = Order.generate_id(_date)#生成ID
        order.user_id = user.user_id
        order.username = user.name
        order.order_type = int(request.form.get('order_type', 1))
        order.order_mode = int(request.form.get('order_mode', 1))
        order.payment_type = int(request.form.get('payment_type', 1))
        link_order_id = int(request.form.get('link_order_id', 0))
        if link_order_id:
            order.link_order_id = link_order_id
        order.item_fee = total_item_fee#TODO:优惠处理
        order.shipping_address_id = address.id

        need_invoice = int(request.form.get('need_invoice', 0))
        if need_invoice:
            order.invoice_name = request.form.get('invoice_name', None)
        order.need_invoice = need_invoice

        discount_fee = request.form.get('discount_fee', 0)
        if not discount_fee: discount_fee = 0
        order.discount_type = int(request.form.get('discount_type', 0))
        order.discount_fee = float(discount_fee)

        order.client_ip = request.form.get('client_ip',None)
        order.remark = request.form.get('remark', None)
        order.user_remark = request.form.get('user_remark',None)
        order.created_by = operator.id
        order.operator_id = operator.id
        order.team = operator.team
        order.update_status(1)
        
        if djjtotle>0:
            order.item_fee -= djjtotle#订单减去代金卷
            order.voucher_fee = djjtotle
            for djjm in djj:
                voucheruser = User_Voucher.query.get(djjm)
                voucheruser.order_id = order.order_id
                order.voucher_id = voucheruser.id
                db.session.add(voucheruser)

        db.session.add(order)
        db.session.flush()

        log = Order_Log()
        log.operator_id = operator.id
        log.order_id = order.order_id
        log.to_status = 1
        log.remark = u'创建订单'
        log.ip = request.remote_addr
        db.session.add(log)
        db.session.flush()

        #订单商品
        # for sku, quantity in _select_items:
        #     sku.order_quantity = Sku.order_quantity + quantity
        #     _order_item = Order_Item()
        #     _order_item.order_id = order.order_id
        #     _order_item.sku_id = sku.id
        #     _order_item.quantity = quantity
        #     _order_item.name = sku.name
        #     _order_item.price = sku.actual_price
        #     _order_item.fee = item_fees[sku.id]
        #     _order_item.unit = sku.unit
        #     _order_item.code = sku.code
        #     db.session.add(_order_item)

        for sku_id,pkg_name,name,price,quantity,fee,unit,code in _order_items:
            _order_item = Order_Item()
            _order_item.order_id = order.order_id
            _order_item.sku_id = sku_id
            _order_item.quantity = quantity
            _order_item.name = name
            _order_item.pkg_name = pkg_name
            _order_item.price = price
            _order_item.fee = fee
            _order_item.unit = unit
            _order_item.code = code
            db.session.add(_order_item)


        #订购套餐
        for sku_set, quantity in _sku_sets:
            _order_sku_set = Order_Sets()
            _order_sku_set.sku_set_id = sku_set.id
            _order_sku_set.name = sku_set.name
            _order_sku_set.order_id = order.order_id
            _order_sku_set.quantity = quantity
            _order_sku_set.price = sku_set.price
            db.session.add(_order_sku_set)

        user.add_order(order)#添加用户订单

        
        db.session.commit()
        return True, order.order_id
    except Exception, e:
        db.session.rollback()
        current_app.logger.error('[order]create failed, error: %s.' % e)
        return False, e.message


# def allowd_order_items():
#     _items = []
#     for sku in Sku.allowed_order_skus():
#         _items.append({'id': sku.id, 'type': 1, 'unit': sku.unit, 'name': sku.name, 'price': sku.actual_price,
#                        'quantity': sku.actual_quantity})
#     for sku_set in Sku_Set.query.filter(Sku_Set.is_valid == True):
#         _items.append(
#             {'id': sku_set.id, 'type': 2, 'unit': u'套', 'name': sku_set.name, 'price': sku_set.price, 'quantity': 0})
#     return _items


@admin.route('/order/clear_order_items')
@admin_required
def clear_order_items():
    cache.set(ALLOWED_ORDER_ITEMS_CACHE_KEY,None,0)
    return 'ok'
def allowed_order_items():
    _data = cache.get(ALLOWED_ORDER_ITEMS_CACHE_KEY)
    if isinstance(_data,list):
        return _data
    _data = Sku.allowed_order_skus()+Sku_Set.allowed_order_skus()
    cache.set(ALLOWED_ORDER_ITEMS_CACHE_KEY,_data,0)
    return _data


@admin.route('/order/add', methods=['GET', 'POST'])
@admin_required
def add_order():
    if request.method == 'POST':
        result, desc = _add_order(current_user, request)
        return jsonify(result=result, desc=desc)
    return render_template('order/add_order.html', items=allowed_order_items())

@admin.route('/order/update_flag/<int:order_id>/<int:flag>', methods=['POST'])
@login_required
def update_order_status_flag(order_id,flag):
    if request.method == 'POST':
        try:
            order = Order.query.get(order_id)
            if not order.status_flag & flag:
                order.status_flag = Order.status_flag+flag
                db.session.commit()
            return jsonify(result=True)
        except:
            return jsonify(result=False,error=u'订单不存在')


@admin.route('/order/update_picker_status',methods=['POST'])
@login_required
def update_order_picker_status():
    order_id = request.form['order_id']
    try:
        order = Order.query.get(order_id)
    except:
        return jsonify(result=False, error=u'订单不存在')
    order.is_picker = True
    db.session.commit()
    return jsonify(result=True)

@admin.route('/order/fast_delivery',methods=['POST','GET'])
@admin_required
def order_fast_delivery():        
    if request.method=='POST':
        express_id = int(request.form['express_id']) 
        orders = Order.query.filter(Order.express_id==express_id,Order.status==4)
        #增加库房的选择物流
        if current_user.role_id in KF_ROOLEIDS:
            orders = Order.query.filter(Order.express_id==express_id,Order.store_id == current_user.store_id,Order.status==4)
        try:
            for order in orders:
                result,desc = _manage_order(order,5,u'一键发货')
                if result is not True:
                    raise Exception(u'处理订单《%s》发生错误：%s'%(order.order_id,desc))
            return jsonify(result=True)
        except Exception,e:
            current_app.logger.error('FAST DELIVERY ERROR.%s'%e)
            return jsonify(result=False,error=e.message)

    objs = db.session.query(Order.express_id,func.count(Order.order_id),func.round(func.sum(Order.item_fee),2),func.sum(Order.discount_fee)).filter(Order.status==4).group_by(Order.express_id).all()
    #增加库房的选择物流
    if current_user.role_id in KF_ROOLEIDS:
        objs = db.session.query(Order.express_id,func.count(Order.order_id),func.round(func.sum(Order.item_fee),2),func.sum(Order.discount_fee)).filter(Order.status==4,Order.store_id == current_user.store_id).group_by(Order.express_id).all()
    express_orders = []
    for express_id,order_nums,item_fee,discount_fee in objs:
        express_orders.append({'express_id':express_id,
                               'express_name':EXPRESS_CONFIG[express_id]['name'],
                               'order_nums':order_nums,
                               'total_fee':item_fee-discount_fee})
    return render_template('order/fast_delivery.html',express_orders = express_orders)


@admin.route('/order/except_orders',methods=['GET','POST'])
def except_orders():
    if request.method == 'POST':
        _id = int(request.form['id'])
        _quantity = int(request.form['quantity'])
        _price = float(request.form['price'])
        _fee = float(request.form['fee'])

        order_item = Order_Item.query.get(_id)
        if not order_item:return jsonify(result=False,error=u'记录不存在')
        order_item.quantity = _quantity
        order_item.price = _price
        order_item.fee = _fee
        db.session.commit()
        return jsonify(result=True)

    rows = db.session.execute('''
SELECT `order`.`order_id`,`order`.status,`order`.item_fee-`order`.discount_fee,CONVERT(`tmp`.total_fee,unsigned int) AS item_fee FROM `order` JOIN
(SELECT `order_id`,SUM(`fee`) as total_fee FROM `order_item` GROUP BY `order_id`) AS tmp
ON `order`.order_id=`tmp`.order_id AND convert(`order`.item_fee-`order`.discount_fee,decimal(5,1))<>convert(`tmp`.total_fee,decimal(5,1))''')
    _orders = {}
    for order_id,status,order_fee,item_fee in rows:
        _orders[order_id] = {'order_id':order_id,
                             'status':ORDER_STATUS[status],
                             'order_fee':order_fee,
                             'item_fee':item_fee,
                             'diff_fee':order_fee-item_fee,
                             'order_items':[]}

    if len(_orders)>0:
        order_items = Order_Item.query.filter(Order_Item.order_id.in_(_orders.keys()))
        for order_item in order_items:
            _orders[order_item.order_id]['order_items'].append(order_item)
    return render_template('order/except_orders.html',orders = _orders.values())




@admin.route('/order/search_phone')
@admin_required
def search_order_phone():
    m = request.args.get('m','')
    code = request.args.get('code','')
    error = ''
    phones = ''
    if m:
        order = Order.query.filter(Order.express_number==m).first()
        while True:
            if not order:
                error = u'订单不存在！'
                break
            if order.code and code <> code:
                error = u'查询码输入错误！'
                break
            if order.status<>5:
                error = u'当前订单状态不允许查询号码！'
                break

            _phones = []
            shipping_address = order.shipping_address
            if shipping_address.phone:_phones.append(shipping_address.phone)
            if shipping_address.tel:_phones.append(shipping_address.tel)
            phones = '<br/>'.join(_phones)
            break
    return render_template('order/search_order_phone.html',error=error,phones=phones)

def order_conditions():
    _conditions = []
    _conditions.append(Order.status < 200)
    order_id = request.args.get('order_id', 0)
    if order_id: _conditions.append(Order.order_id == int(order_id))

    username = request.args.get('name', None)
    if username: _conditions.append(User.name.like('%' + username + '%'))

    op_id = request.args.get('op',None)
    if op_id:
        _conditions.append(Order.created_by==int(op_id))

    phone = request.args.get('phone', None)
    if phone:
        _conditions.append(Order.user_id==User_Phone.user_id_by_phone(phone))

    express_id = request.args.get('express_id',0)
    if express_id:
        _conditions.append(Order.express_id==int(express_id))

    payment_type = request.args.get('payment_type',0)
    if payment_type:
        _conditions.append(Order.payment_type==int(payment_type))

    express_number = request.args.get('express_number', None)
    if express_number: _conditions.append(Order.express_number == express_number)

    _start_date = request.args.get('start_date','')
    _end_date = request.args.get('end_date','')

    history_status = int(request.args.get('history_status',0))
    status = int(request.args.get('order_status', 0))
    #订单状态过滤
    if not history_status:
        if status:_conditions.append(Order.status == status)
        if _start_date:_conditions.append(Order.modified>=_start_date)
        if _end_date:_conditions.append(Order.modified<=_end_date)
    else:
        if status:
            _log_conditions = [Order_Log.to_status==status]
            if _start_date:_log_conditions.append(Order_Log.operate_time>=_start_date)
            if _end_date:_log_conditions.append(Order_Log.operate_time<=_end_date)
            _conditions.append(db.or_(Order.order_id.in_(db.session.query(Order_Log.order_id).filter(*_log_conditions))))
        else:
            if _start_date:_conditions.append(Order.created>=_start_date)
            if _end_date:_conditions.append(Order.created<=_end_date)

    return _conditions


@admin.route('/order/approval')
@admin_required
def order_approval():
    #订单状态过滤
    if not ROLE_ALLOWED_ORDER_STATUS.has_key(current_user.role_id):
        return render_template('order/orders_new.html', pagination=Pagination(None, 1, 10, 0, []), show_query=True)

    page = int(request.args.get('page', 1))

    per_page = request.args.get('per_page','')
    if per_page:
        PER_PAGE = int(per_page)
    else:
        PER_PAGE = 10

    _conditions = []
    # if current_user.role_id == ORDER_ROLE_ID:
    #     _conditions.append(Order.created_by == current_user.id)
    # else:
    #     _conditions.append(Order.assign_operator_id == current_user.id)

    _conditions.append(Order.assign_operator_id == current_user.id)
        # allowed_status = ROLE_ALLOWED_ORDER_STATUS[current_user.role_id]
        # _conditions.append(Order.status.in_(allowed_status))
    _conditions.extend(order_conditions())
    #增加库房的选择物流
    if current_user.role_id in KF_ROOLEIDS:
        _conditions.append(Order.store_id == current_user.store_id)

    #base_query =
    if current_user.role_id == ORDER_ROLE_ID:
        pagination = Order.query.join(User, Order.user_id == User.user_id).filter(db.and_(*_conditions)).order_by(
            desc(Order.created)).paginate(page, per_page=PER_PAGE)
    else:
        pagination = Order.query.join(User, Order.user_id == User.user_id).filter(db.and_(*_conditions)).order_by(
            asc(Order.modified)).paginate(page, per_page=PER_PAGE)
    return render_template('order/orders_new.html', pagination=pagination, show_query=True)




@admin.route('/order/list')
@admin_required
def orders():
    _conditions = order_conditions()

    if not current_user.is_admin:
        #仅允许员工查看自己订单
        if current_user.role_id == ORDER_ROLE_ID:
            _conditions.append(Order.created_by == current_user.id)
        else:#仅允许查看分配的订单
            #_conditions.append(Order.assign_operator_id == current_user.id)            
            if len(_conditions)==0 or not current_user.action('order_search'):
                #_conditions.append(db.and_(Order.team.like(current_user.team[0] + '%')))#只能看到本组的数据
                _conditions.append(db.or_(Order.assign_operator_id == current_user.id,
                                         Order.order_id.in_(db.session.query(Order_Log.order_id).filter(Order_Log.operator_id==current_user.id))))
    #增加库房的选择物流
    if current_user.role_id in KF_ROOLEIDS:
        _conditions.append(Order.store_id == current_user.store_id)
    page = int(request.args.get('page', 1))

    per_page = request.args.get('per_page','')
    if per_page:
        PER_PAGE = int(per_page)
    else:
        PER_PAGE = 10

    if len(_conditions) > 0:
        pagination = Order.query.join(User, Order.user_id == User.user_id).filter(db.and_(*_conditions)).order_by(
            desc(Order.created)).paginate(page, per_page=PER_PAGE)
    else:
        pagination = Order.query.join(User, Order.user_id == User.user_id).order_by(desc(Order.created)).paginate(page,per_page=PER_PAGE)
    print pagination
    ops = db.session.query(Operator.id,Operator.nickname).filter(Operator.role_id.in_(SEE_ORDER_ROLE_ID),Operator.status<>9)
    print ORDER_ROLE_ID
    return render_template('order/orders_new.html', pagination=pagination, show_query=True, ops = [(op_id,name) for op_id,name in ops])


@admin.route('/order/change_order_op',methods=['POST'])
@admin_required
def change_order_op():
    try:
        sel_ids = json.loads(request.form['ids'])
        op_id = int(request.form['op_id'])
        order_ids = map(lambda s:int(s),sel_ids)
        if len(order_ids)==0:return jsonify(result=False,error=u'请先选择要变更归属的订单！')
        orders = Order.query.filter(Order.order_id.in_(order_ids))

        op = Operator.query.get(op_id)
        if op.role_id<>ORDER_ROLE_ID:return jsonify(result=False,error=u'该员工不允许被指派订单')
        for order in orders:
            if order.created_by == op_id:continue
            current_app.logger.info('CHANGE_ORDER_OP|%s|%s|%s|%s'%(current_user.id,order.order_id,order.created_by,op.id))
            if order.assign_operator_id<>op.id and order.assign_role_id==ORDER_ROLE_ID:
                order.assign_operator_id = op.id
            order.operator_id = op.id
            order.created_by = op.id
            order.team = op.team
            #add john 增加修改归属人记录
            order_operator = Order_Operator()
            order_operator.order_id = order.order_id
            order_operator.operator_id = current_user.id
            order_operator.to_operator_id = op_id
            order_operator.remark = '更改归属人'
            order_operator.ip = request.remote_addr
            db.session.add(order_operator)
        db.session.commit()
        return jsonify(result=True)
    except Exception,e:
        printException()
        db.session.rollback()
        current_app.logger.error('CHANGE ORDER OPERATOR ERROR.%s'%e)
        return jsonify(result=False,error=e.message)



def _manage_order(order,to_status,remark='',sf_id='',express_sfdestcode=0,express_sfok=0):
    _allows = filter(lambda a: a[2] == to_status and a[3] & order.payment_type, ORDER_OPROVRAL_CONFIG[order.status])
    if len(_allows) <> 1: return False,u'未允许操作'
    op_name, css, to_status, payment_type, flag = _allows[0]

    if order.status == 2 and to_status in (3, 40,):#内勤审核
        store_id = int(request.form['store_id'])
        express_id = request.form.get('express_id', 0)
        if not express_id:
            return False,u'请先选择物流公司'

        #--->验证订单商品库存是否满足条件
        _item_amounts = Order_Item.order_item_amount(order.order_id)
        _store_amounts = {}
        sku_stocks = Sku_Stock.query.filter(Sku_Stock.sku_id.in_(_item_amounts.keys()),
                                            Sku_Stock.store_id==store_id)
        for sku_stock in sku_stocks:
            _store_amounts[sku_stock.sku_id] = sku_stock

        for sku_id,amount in _item_amounts.iteritems():
            if not _store_amounts.has_key(sku_id):
                return False,u'所选仓库部分商品无货！'

            _sku_stock = _store_amounts[sku_id]
            if _sku_stock.actual_quantity-amount<_sku_stock.threshold:
                return False,u'所选仓库部分商品库存不足！'

            _sku_stock.order_quantity = Sku_Stock.order_quantity + amount

        order.store_id = store_id
        order.express_id = int(express_id)

    elif order.status == 40 and to_status == 4:
        if sf_id=='':
            express_num = request.form.get('express_num', 0)
            if not express_num:
                return False,u'请先输入快递单号'
            order.express_number = express_num            
        else:
            order.express_number = sf_id
            order.express_sfdestcode = express_sfdestcode
            order.express_sfok = express_sfok
    elif order.status == 4 and to_status == 40:#取消快递        
        order.express_number = ''
        order.express_sfdestcode = ''
        order.express_sfok = 0


    #库存处理
    if flag == 1:#--->出库
        _item_amounts = Order_Item.order_item_amount(order.order_id)
        _store_amounts = {}
        sku_stocks = Sku_Stock.query.filter(Sku_Stock.sku_id.in_(_item_amounts.keys()),
                                            Sku_Stock.store_id==order.store_id)
        for sku_stock in sku_stocks:
            _store_amounts[sku_stock.sku_id] = sku_stock

        for sku_id,amount in _item_amounts.iteritems():
            if not _store_amounts.has_key(sku_id):
                db.session.rollback()
                return False,u'商品库存数量不足，无法出库！'

            _sku_stock = _store_amounts[sku_id]
            if _sku_stock.quantity<amount:
                db.session.rollback()
                return False,u'商品库存数量不足，无法出库！'
            _sku_stock.order_quantity = Sku_Stock.order_quantity - amount
            _sku_stock.quantity = Sku_Stock.quantity - amount
            Stock_Out.sale(order,sku_id,amount,order.store_id)#出库

    elif flag == 2:#--->入库
        return_items = json.loads(request.form['return-items'])
        _return_items = {}
        for k, d in return_items.iteritems():
            _return_items[int(k)] = int(d.get('in', 0)), int(d.get('loss', 0))

        order_items = order.order_items
        _in_return_items = defaultdict(int)
        for order_item in order_items:
            if not _return_items.has_key(order_item.id): continue
            in_quantity, loss_quantity = _return_items[order_item.id]

            if in_quantity>order_item.quantity:return False,u'退货入库数量错误！'
            if in_quantity>0:
                order_item.in_quantity = in_quantity
                _in_return_items[order_item.sku_id] += in_quantity
            if loss_quantity>0:order_item.loss_quantity = loss_quantity

        for sku_id,amount in _in_return_items.iteritems():
            Stock_In.sale_return(order.order_id,sku_id,amount,order.store_id)

    elif order.status>2 and to_status==1 and order.store_id:#订单打回(撤销库房销售数量)
        _item_amounts = Order_Item.order_item_amount(order.order_id)
        for sku_id,amount in _item_amounts.iteritems():
            Sku_Stock.query.filter(db.and_(Sku_Stock.store_id==order.store_id,
                                           Sku_Stock.sku_id==sku_id)).update({'order_quantity':Sku_Stock.order_quantity-amount})

        order.express_number = None
        order.express_id = None


    order_log = Order_Log()
    order_log.operator_id = current_user.id
    order_log.remark = remark
    order_log.to_status = to_status
    order_log.order_id = order.order_id
    order_log.ip = request.remote_addr
    db.session.add(order_log)
    if order.user.qxhdm_user_id > 0 and to_status == 6 and order.status == 5:
        bigcount = 0
        mediumcount = 0
        smallcount = 0
        for oi in order.order_items:
            if oi.sku_id == 10003:
                bigcount += oi.quantity
            if oi.sku_id == 10002:
                mediumcount += oi.quantity
            if oi.sku_id == 10001:
                smallcount += oi.quantity
        if bigcount > 0 or mediumcount > 0 or smallcount > 0:
            html = StringIO()
            url = r'%supdateqxh?id=%s&order_id=%s&bigcount=%s&mediumcount=%s&smallcount=%s'%(DMURL,order.user.qxhdm_user_id,order.order_id,bigcount,mediumcount,smallcount)
            print url
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.SSL_VERIFYHOST, False)
            c.setopt(pycurl.SSL_VERIFYPEER, False)
            c.setopt(pycurl.WRITEFUNCTION, html.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.perform()
    #DM单
    if to_status == 6 and order.status == 5:
        dmd = 0
        #print 'ok'
        for oi in order.order_items:
            #print 'ok2'
            if oi.sku_id == DMD_ID:
                dmd = 1
                #print 'ok3'
                break
        if dmd:            
            #print 'ok4'
            #print order.order_id
            voucheruser = User_Voucher();
            voucheruser.user_id = order.user_id
            voucheruser.operator_id = 1
            voucheruser.remark = order.order_id
            voucheruser.price = 20
            voucheruser.status = True
            db.session.add(voucheruser)
    print order.assign_operator_id

    order.update_status(to_status)

        
    order.operate_log = remark
    order.modified = datetime.now()
    print 'ok'
    print order.assign_operator_id
    db.session.commit()
    current_app.logger.info('ORDER|MANAGE|%s|%d|%d|%s'%(order.order_id,current_user.id,to_status,remark))
    return True,''


@admin.route('/order/manage/<int:order_id>', methods=['POST'])
@admin_required
def manage_order(order_id):
    to_status = int(request.form['status'])
    remark = request.form['remark']
    try:
        order = Order.query.get(order_id)
    except:
        return jsonify(result=False, error=u'订单不存在')

    if not ORDER_OPROVRAL_CONFIG.has_key(order.status):
        return jsonify(result=False, error=u'非法操作')

    #检测是否授权
    if not order.is_authorize(current_user):
        return jsonify(result=False, error=u'权限不足，无法执行该操作')
    result,desc = _manage_order(order,to_status,remark)
    return jsonify(result=result,error=desc)

@admin.route('/order/sf/', methods=['POST'])
@admin_required
def sf_order():
    order_id = int(request.form['order_id'])
    try:
        order = Order.query.get(order_id)
    except:
        return jsonify(result=False, error=u'订单不存在')

    if not ORDER_OPROVRAL_CONFIG.has_key(order.status):
        return jsonify(result=False, error=u'非法操作')

    #检测是否授权
    if not order.is_authorize(current_user):
        return jsonify(result=False, error=u'权限不足，无法执行该操作')
    client = suds.client.Client(SF_Url)
    client.set_options(headers={"Content-Type":"text/xml; charset=utf-8"})
    print 'ok'
    print order.payment_type
    sfcity = ' d_province=\''+order.shipping_address.province+'\' d_city=\''+order.shipping_address.city+'\''
    
    sfgod = ''
    if order.payment_type == 1 and order.actual_fee > 0:
        sfgod = '<AddedService name=\'COD\' value=\''+str(order.actual_fee)+'\' value1=\'0283439931\' value2=\'\' value3=\'\' value4=\'\' /> '
    SF_Order = 'orderid=\''+str(order_id)+'\' express_type=\'3\' '
    custid = 'custid=\''+SF_Custid+'\''
    strxml = '''<Request service='OrderService' lang='zh-CN'>
        <Head>'''+SF_Custid+''','''+SF_Key+'''</Head><Body>
         <Order 
                  '''+SF_Order+SF_D+sfcity+'''                  
d_company=''
                  d_contact='
'''+order.shipping_address.ship_to+'''
'
                  d_tel='
'''+str(order.shipping_address.phone)+str(order.shipping_address.tel)+'''
'
                  d_address='
'''+order.shipping_address.format_address+'''
'
                  parcel_quantity='1'
                  pay_method='1'>
<OrderOption '''+custid+''' >'''+sfgod+'''
                    </OrderOption>   
                   </Order></Body>
         </Request> 
        '''
    results = client.service.sfexpressService(strxml)
    doc = minidom.parseString(results)
    root = doc.documentElement
    #print 'ok'+results
    #print strxml
    #current_app.logger.error(u'strxml:%s' % (strxml))
    current_app.logger.error(u'results:%s,%s' % (str(order_id),results))
    OrderResponse = root.getElementsByTagName("OrderResponse")
    if len(OrderResponse) > 0:
        #print 'ok2'
        sf_id = OrderResponse[0].getAttribute('mailno')
        if order.shipping_address.province == '北京市':
            express_sfdestcode = '010'
        elif order.shipping_address.province == '上海市':
            express_sfdestcode = '021'
        elif order.shipping_address.province == '天津市':
            express_sfdestcode = '022'
        elif order.shipping_address.province == '重庆市':
            express_sfdestcode = '023'
        elif order.shipping_address.province == '新疆维吾尔自治区':
            express_sfdestcode = '991'
        else:
            express_sfdestcode = OrderResponse[0].getAttribute('destcode')
        
        #生成条形码
        #发货确认
        confirmxml = '''<Request service='OrderConfirmService' lang='zh-CN'>
<Head>%s,%s</Head>
         <Body>
         <OrderConfirm  mailno='%s' orderid='%s'>
           </OrderConfirm>
           </Body>
        </Request>
'''%(SF_Custid,SF_Key,sf_id,str(order_id))
        #print confirmxml
        results = client.service.sfexpressService(confirmxml)
        #print results
        current_app.logger.error(u'qrresults:%s,%s' % (str(order_id),results))
        doc = minidom.parseString(results)
        root = doc.documentElement
        OrderConfirmResponse = root.getElementsByTagName("OrderConfirmResponse")
        if len(OrderResponse) > 0:
            result,desc = _manage_order(order,4,u'顺风拣货',sf_id,express_sfdestcode,1)
            return jsonify(result=result,error=desc)
        else:
            result,desc = _manage_order(order,4,u'顺风拣货',sf_id,express_sfdestcode,0)
            return jsonify(result=False,error='顺风发货确认失败')
    else:
        return jsonify(result=False,error=u'顺风接口错误')

@admin.route('/order/sfquxiao/', methods=['POST'])
@admin_required
def sf_quxiao():
    order_id = int(request.form['order_id'])
    try:
        order = Order.query.get(order_id)
    except:
        return jsonify(result=False, error=u'订单不存在')

    if not ORDER_OPROVRAL_CONFIG.has_key(order.status):
        return jsonify(result=False, error=u'非法操作')

    #检测是否授权
    if not order.is_authorize(current_user):
        return jsonify(result=False, error=u'权限不足，无法执行该操作')
    
    #发货确认
    confirmxml = '''<Request service='OrderConfirmService' lang='zh-CN'>
<Head>%s,%s</Head>
     <Body>
     <OrderConfirm  mailno='%s' orderid='%s'>
       </OrderConfirm>
       </Body>
    </Request>
'''%(SF_Custid,SF_Key,order.express_number,str(order_id))
    print confirmxml
    client = suds.client.Client(SF_Url)
    results = client.service.sfexpressService(confirmxml)
    print results
    doc = minidom.parseString(results)
    root = doc.documentElement
    OrderConfirmResponse = root.getElementsByTagName("OrderConfirmResponse")
    if len(OrderResponse) > 0:    
        result,desc = _manage_order(order,40,u'取消快递')
        return jsonify(result=result,error=desc)
    else:
        return jsonify(result=False,error=u'取消快递失败')

@admin.route('/order/printsf/<int:order_id>', methods=['POST', 'GET'])
@admin_required
def print_sf(order_id):
    order = Order.query.get(order_id)
    ocount = 0
    for oi in order.order_items:
        ocount+=oi.quantity
    if order.order_type==14 or order.order_type==15 or order.order_type==16:
        return render_template('order/print_sfxlj.html',ocount=ocount, order=order, datat=datetime.now().strftime('%Y-%m-%d'))
    else:
        return render_template('order/print_sf.html',ocount=ocount, order=order, datat=datetime.now().strftime('%Y-%m-%d'))

@admin.route('/order/creattxm', methods=['POST', 'GET'])
@admin_required
def creattxm():
    a = barcode('qrcode','Hello Barcode Writer In Pure PostScript.',options=dict(version=9, eclevel='M'),margin=10, data_mode='8bits')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    #qr = qrcode.QRCode(a)
    qr.add_data('ok')
    qr.make(fit=False)        
    img = qr.make_image()
    a = barcode('qrcode','Hello Barcode Writer In Pure PostScript.',options=dict(version=9, eclevel='M'),margin=10, data_mode='8bits')
    
    a.save('./static/qrcode/'+'15.jpg')
    return 'ok'
    

def _edit_order(order):
    try:
        if order.status not in ORDER_ALLOWED_EDIT_STATUS:
            return False, u'当前状态禁止修改订单信息！'
        is_xlj = False
        items_changed = int(request.form['items_changed'])
        #代金卷
        _conditions = []
        _conditions.append(User_Voucher.order_id == order.order_id)
        voucherusers = User_Voucher.query.filter(db.and_(*_conditions)).all()
        for vu in voucherusers:
            vu.order_id = None
            db.session.add(vu)
        order.voucher_fee = 0
        djj = json.loads(request.form['djj2'])
        djjlen = len(djj)

        djjtotle = 20*djjlen
        order.voucher_fee = djjtotle
        if djjlen > 0:
            for djjm in djj:
                voucheruser = User_Voucher.query.get(djjm)
                if voucheruser.user_id<>order.user_id or voucheruser.order_id>0:return False, '不能使用该代金卷'
                voucheruser.order_id = order.order_id



        if items_changed:
            items = json.loads(request.form['items'])

            for item_id, data in items.iteritems():
                _id = int(data['sku-id'])
                if _id==XLJ_ID:
                    is_xlj=True
                    break

            if len(items) == 0: return False, u'选择商品不可为空'

            total_item_fee = 0
            totalitemfee = 0
            _sku_objs = {}
            _sku_sets = []
            _order_items = []
            for item_id, data in items.iteritems():
                quantity = int(data['quantity'])
                if quantity <= 0: return False, u'商品数量不正确'
                _type = data['type']
                _price = float(data['price'])
                _name = data['name']
                _id = int(data['sku-id'])
                if _type == 1:
                    if _sku_objs.has_key(_id):
                        _sku = _sku_objs[_id]
                    else:
                        _sku = Sku.query.get(_id)
                        _sku_objs[_sku.id] = _sku

                    if _price not in _sku.allowed_prices:
                        return False,u'商品《%s》不允许使用价格：%s!'%(_sku.name,_price)

                    _fee = _price * quantity
                    total_item_fee += _fee
                    totalitemfee += _fee
                    _order_items.append((_sku.id,'',_name,_price,quantity,_fee,_sku.unit,_sku.code))
                else:
                    _sku_set = Sku_Set.query.get(_id)
                    if not _sku_set.is_valid: return False, u'套餐《%s》当前未启用！' % _sku_set.name
                    _sku_price_config = _sku_set.price_config
                    for sku_id, per_quantity in _sku_set.config.iteritems():
                        if _sku_objs.has_key(sku_id):
                            _sku = _sku_objs[sku_id]
                        else:
                            _sku = Sku.query.get(sku_id)
                            _sku_objs[_sku.id] = _sku
                        _quantity = per_quantity*quantity
                        item_price = _sku_set.price_config[_sku.id]
                        _fee = item_price * _quantity
                        _order_items.append((_sku.id,_sku_set.name,_sku.name,item_price,_quantity,_fee,_sku.unit,_sku.code))
                    total_item_fee += _sku_set.price * quantity
                    totalitemfee += _sku_set.price * quantity
                    _sku_sets.append((_sku_set, quantity))

            #扣减原有销售数量
            for order_item in order.order_items:
                sku = order_item.sku
                sku.order_quantity = Sku.order_quantity - order_item.quantity
                db.session.delete(order_item)

            db.session.query(Order_Sets).filter(Order_Sets.order_id == order.order_id).delete()#删除套餐
            db.session.flush()

            #订单商品
            for sku_id,pkg_name,name,price,quantity,fee,unit,code in _order_items:
                _order_item = Order_Item()
                _order_item.order_id = order.order_id
                _order_item.sku_id = sku_id
                _order_item.quantity = quantity
                _order_item.name = name
                _order_item.pkg_name = pkg_name
                _order_item.price = price
                _order_item.fee = fee
                _order_item.unit = unit
                _order_item.code = code
                db.session.add(_order_item)

            #订购套餐
            for sku_set, quantity in _sku_sets:
                _order_sku_set = Order_Sets()
                _order_sku_set.sku_set_id = sku_set.id
                _order_sku_set.name = sku_set.name
                _order_sku_set.order_id = order.order_id
                _order_sku_set.quantity = quantity
                _order_sku_set.price = sku_set.price
                db.session.add(_order_sku_set)

            order.item_fee = total_item_fee#TODO:优惠处理
            #if djj > 0:                
                #if totalitemfee<voucheruser.price:return False, '不能使用该代金卷1'                
                #order.item_fee -= voucheruser.price #订单减去代金卷

        if djjlen > 0:
            if voucherusers:#以前有 现在有
                if items_changed:
                    order.item_fee -= djjtotle #订单减去代金卷
                else:
                    order.item_fee -= (djjtotle-len(voucherusers)*20) 
            else:#以前没有 现在有
                order.item_fee -= djjtotle #订单减去代金卷 
        else:
            if voucherusers:#以前有  现在没有
                order.voucher_id = 0
                if items_changed:
                    pass
                else:
                    order.item_fee += len(voucherusers)*20 #订单增加代金卷


        order.is_xlj = is_xlj
        order.order_type = int(request.form.get('order_type', 1))
        order.order_mode = int(request.form.get('order_mode', 1))
        order.payment_type = int(request.form.get('payment_type', 1))
        need_invoice = int(request.form.get('need_invoice', 0))
        if need_invoice:
            order.invoice_name = request.form.get('invoice_name', None)
        order.need_invoice = need_invoice

        discount_fee = request.form.get('discount_fee', 0)
        if not discount_fee: discount_fee = 0
        order.discount_type = int(request.form.get('discount_type', 0))
        order.discount_fee = float(discount_fee)

        order.client_ip = request.form.get('client_ip',None)
        order.remark = request.form.get('remark', None)
        order.user_remark = request.form.get('user_remark', None)
        #order.modified = datetime.now()
        db.session.commit()
        return True, u'修改成功'
    except Exception, e:
        db.session.rollback()
        current_app.logger.error(u'edit order(ID:%s) error:%s' % (order.order_id, e))
        return False, u'修改订单失败'


@admin.route('/order/edit/<int:order_id>', methods=['POST', 'GET'])
@admin_required
def edit_order(order_id):
    order = Order.query.get(order_id)
    _conditions = []
    _conditions.append(User_Voucher.order_id == order_id)
    voucheruser = User_Voucher.query.filter(db.and_(*_conditions))


    if request.method == 'POST':
        result, desc = _edit_order(order)
        if result:
            current_app.logger.info('ORDER|EDIT|%s|%s'%(order.order_id,current_user.id))
        return jsonify(result=result, error=desc)
    return render_template('order/edit_order.html', order=order,voucheruser=voucheruser, items=allowed_order_items())

@admin.route('/order/user/<int:user_id>')
@login_required
def user_orders(user_id):
    orders = Order.query.filter(db.and_(Order.user_id==user_id,Order.status<=100)).order_by(desc(Order.created))
    _datas = []
    for o in orders:
        _datas.append({'id':o.order_id,
                       'time':o.created.strftime('%Y-%m-%d %H:%M:%S'),
                       'fee':o.actual_fee,
                       'payment':o.payment_type_name,
                       'status':o.status_name,
                       'op_name':o.publisher.nickname})

    _order_items = []
    if len(_datas)>0:
        order_items = db.session.query(Order_Item.sku_id,
                                       Order_Item.name,
                                       Order_Item.price,
                                       func.sum(Order_Item.quantity),
                                       func.sum(Order_Item.fee)).join(Order,Order.order_id==Order_Item.order_id).filter(Order.user_id==user_id,Order.status<=100).group_by(Order_Item.sku_id,
                                                                                                                                                         Order_Item.name,
                                                                                                                                                         Order_Item.price)
        for sku_id,name,price,quantity,fee in order_items:
            _order_items.append({'sku_id':sku_id,'name':name,'price':price,'quantity':quantity,'fee':fee})
    return jsonify(orders=_datas,order_items=_order_items)


@admin.route('/order/detail/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    logs = Order_Log.log_by_order_id(order_id)

    is_auth = True
    if not current_user.is_admin and not current_user.action('order_search') and order.assign_operator_id<>current_user.id:
        is_auth = False
        for log in logs:
            if log['id']==current_user.id:
                is_auth = True
    return render_template('order/order_detail.html', order=order, logs=logs,is_auth=is_auth)


@admin.route('/order/print/invoices/<int:order_id>')
@admin_required
def print_order_invoices(order_id):
    order = Order.query.get_or_404(order_id)
    date = datetime.now().strftime("%Y/%m/%d")
    if order.is_xlj:
        return render_template('order/print_invoices_xlj.html', orders=[order], date=date)
    else:
        return render_template('order/print_invoices.html', orders=[order], date=date)
    


@admin.route('/order/print/invoices/batch',methods=['POST'])
@login_required
def batch_print_invoices():
    if request.method == 'POST':
        date = datetime.now().strftime("%Y/%m/%d")
        order_ids = json.loads(request.form['print_ids'])
        orders = Order.query.filter(db.and_(Order.order_id.in_(order_ids),Order.status==40))
        try:
            for order in orders:
                if not order.status_flag & 1:
                    order.status_flag = Order.status_flag + 1
            db.session.commit()
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('update order flag error')
    return render_template('order/print_invoices.html',orders=orders,date=date)


def user_order_by():
    is_order = True
    sort_name = request.args.get('sort_name','')
    if not sort_name:
        sort_name = 'join_time'
        is_order = False

    sort_sc = request.args.get('sort_sc',0)
    sort_sc = int(sort_sc)
    _sort = asc if sort_sc==0 else desc
    return is_order,_sort(getattr(User,sort_name))


def user_per_page():
    per_page = request.args.get('per_page','')
    if per_page:
        return int(per_page)
    return 20


def user_conditions():
    _conditions = []    
    #_conditions.append(User.qxhdm_user_id==0)    
    assign_operator_id = request.args.get('assign_operator_id','')
    if assign_operator_id:
        _conditions.append(User.assign_operator_id==int(assign_operator_id))

    username = request.args.get('name', None)
    if username: _conditions.append(User.name.like('%' + username + '%'))

    phone = request.args.get('phone', None)
    if phone:
        _conditions.append(User.user_id == User_Phone.user_id_by_phone(phone))

    intent_level = request.args.get('intent_level', '')
    if intent_level:
        _conditions.append(User.intent_level == intent_level)

    user_type = request.args.get('user_type', 0)
    if user_type:
        _conditions.append(User.user_type == int(user_type))

    product_intention = request.args.get('product_intention', None)
    if product_intention:
        _conditions.append(User.product_intention == int(product_intention))

    label_id = request.args.get('label_id', 0)
    if label_id:
        _conditions.append(User.label_id == int(label_id))

    assign_start = request.args.get('assign_start','')
    if assign_start:
        _conditions.append(User.assign_time >= assign_start)

    assign_end = request.args.get('assign_end','')
    if assign_end:
        _conditions.append(User.assign_time <= assign_end)

    batch_id = request.args.get('batch_id','')
    if batch_id:
        _conditions.append(User.batch_id==batch_id)

    user_remark = request.args.get('user_remark','')
    if user_remark:
        _conditions.append(User.remark.like('%'+user_remark+'%'))

    is_assigned = request.args.get('is_assigned', '')
    if is_assigned:
        is_assigned = int(is_assigned)
        if is_assigned == 1:
            _conditions.append(User.is_assigned == False)
        elif is_assigned == 2:
            _conditions.append(User.is_assigned == True)

    is_abandon = request.args.get('is_abandon', '')
    if is_abandon:
        is_abandon = int(is_abandon)
        if is_abandon == 1:
            _conditions.append(User.is_abandon == True)
        elif is_abandon == 2:
            _conditions.append(User.is_abandon == False)

    user_origin = request.args.get('user_origin', 0)
    if user_origin:
        _conditions.append(User.origin == int(user_origin))
    return _conditions


@admin.route('/user/my')
@admin_required
def my_users():
    _conditions = user_conditions()
    _conditions.append(User.assign_operator_id==current_user.id)
    list_type=int(request.args.get('list_type',3))
    if list_type == 1:
        _conditions.append('user.user_id in (select (u.user_id) from `user` u join `order` o on o.user_id=u.user_id where u.batch_id IS NULL AND u.user_type=2 and datediff(now(),o.created)<=90)')
    if list_type == 0:
        _conditions.append('user.user_id in (select (u.user_id) from `user` u join `order` o on o.user_id=u.user_id where u.batch_id IS NULL AND u.user_type=2 and u.user_id not in (select user_id from `order` where datediff(now(),created)<=90))')
    #add john 
    show_queries = ['list_type','username','phone','user_origin']
    if current_user.id==4:
        show_queries = ['admin','list_type','username','phone','user_origin']

    page = int(request.args.get('page', 1))
    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User.expect_time)
    pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(db.and_(*_conditions)).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/users.html',
                           pagination=pagination,
                           list_type=list_type,
                           show_label = True,
                           operators=Operator.query.filter(Operator.assign_user_type==1),
                           show_queries=show_queries)


def public_users(user_type):
    _conditions = user_conditions()
    _conditions.append(User.user_type==user_type)
    _conditions.append(User.assign_operator_id == None)
    if user_type==5:
        area = request.args.get('area','')
        if area:
            _conditions.append('`user`.area="%s"'%area)
        promoters = request.args.get('promoters','')
        if promoters:
            _conditions.append('`user`.promoters="%s"'%promoters)
        pharmacy = request.args.get('pharmacy','')
        if pharmacy:
            _conditions.append('`user`.pharmacy="%s"'%pharmacy)

    page = int(request.args.get('page', 1))
    is_order,order_by = user_order_by()
    if not is_order:order_by = asc(User.is_assigned)
    pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(db.and_(*_conditions)).order_by(order_by).paginate(page, per_page=user_per_page())
    show_queries=['admin','username','phone','show_assign','user_origin','show_abandon']
    areas = ''
    promoterss = ''
    pharmacys = ''
    if user_type==5:
        areas = db.session.execute('select distinct area from user where qxhdm_time > 0')
        promoterss = db.session.execute('select distinct promoters from user where qxhdm_time > 0')
        pharmacys = db.session.execute('select distinct pharmacy from user where qxhdm_time > 0')
        show_queries=['admin','service','username','phone','show_assign','user_origin','show_abandon']
    return render_template('user/users.html',
                           pagination=pagination,
                           show_label = True if user_type==1 else False,
                           operators=Operator.query.filter(Operator.assign_user_type==user_type),
                           show_queries=show_queries,areas=areas,pharmacys=pharmacys,promoterss=promoterss)

@admin.route('/user/public/new')
@admin_required
def public_new_users():
    return public_users(1)

@admin.route('/user/public/old')
@admin_required
def public_old_users():
    return public_users(2)

@admin.route('/user/public/service')
@admin_required
def public_service_users():
    return public_users(5)


@admin.route('/user/search')
@admin_required
def search_user():
    phone = request.args.get('m')
    if phone:
        if phone.startswith('01') and len(phone)==12:#去除手机号前面的“0”
            phone = phone[1:]
        elif phone.startswith('028'):phone=phone[3:]

        user_id = User_Phone.user_id_by_phone(phone)
        if user_id:
            return redirect(url_for('admin.user',user_id=user_id,token=des.user_token(user_id)))
        else:
            return redirect(url_for('admin.add_user',phone=phone))
    else:
        return redirect(url_for('admin.add_user'))


@admin.route('/user/search_form')
@login_required
def search_user_form():
    return render_template('user/search_user.html')


@admin.route('/user/manage')
@admin_required
def manage_users():
    _conditions = user_conditions()

    #仅允许管理本部门员工数据
    if not current_user.is_admin and current_user.team:
        operators = Operator.query.filter(db.and_(Operator.team.like(current_user.team+'%'),Operator.assign_user_type>0,Operator.status<>9))
        op_ids = [op.id for op in operators]
        _conditions.append(User.assign_operator_id.in_(op_ids))
    else:
        operators = Operator.query.filter(Operator.assign_user_type>0,Operator.status<>9)

    page = int(request.args.get('page', 1))

    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User.join_time)
    if len(_conditions) > 0:
        pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(db.and_(*_conditions)).order_by(order_by).paginate(page, per_page=user_per_page())
    else:
        pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/users.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])



@admin.route('/user/manage/change_op',methods=['POST'])
@admin_required
def change_user_op():
    try:
        sel_ids = json.loads(request.form['ids'])
        op_id = int(request.form['op_id'])
        user_ids = map(lambda s:int(s),sel_ids)
        if len(user_ids)==0:return jsonify(result=False,error=u'请先选择要变更归属的客户！')
        users = User.query.filter(User.user_id.in_(user_ids))
        op = Operator.query.get(op_id)
        # for u in users:
        #     if not op.assign_user_type&u.user_type:
        #         return jsonify(result=False,error=u'员工《%s》指派类型和客户《%s》当前类型不匹配！'%(op.nickname,u.name))

        for u in users:
            current_app.logger.info('CHANGE_USER_OP|%s|%s|%s|%s'%(current_user.id,op_id,u.user_id,u.assign_operator_id))
            if current_user.id==4 and u.assign_operator_id == None and u.user_type==1 and u.origin==1 and u.label_id==1:
                outbound = Outbound()
                outbound.user_id = u.user_id
                db.session.add(outbound)
            u.assign_op(op,current_user.id)
        db.session.commit()
        return jsonify(result=True)
    except Exception,e:
        printException()
        db.session.rollback()
        current_app.logger.error('CHANGE USER OPERATOR ERROR.%s'%e)
        return jsonify(result=False,error=e.message)


@admin.route('/user/manage/change_type',methods=['POST'])
@admin_required
def change_user_type():
    try:
        user_type = int(request.form['user_type'])
        if not USER_TYPES.has_key(user_type):return jsonify(result=False,error=u'未知的客户类型！')
        sel_ids = json.loads(request.form['ids'])
        user_ids = map(lambda s:int(s),sel_ids)
        if len(user_ids)==0:return jsonify(result=False,error=u'请先选择要变更类型的客户！')
        users = User.query.filter(User.user_id.in_(user_ids))
        for u in users:
            if u.user_type<>user_type:
                current_app.logger.info('CHANGE_USER_TYPE|%s|%s|%s|%s'%(current_user.id,u.user_id,u.user_type,user_type))
                u.user_type = user_type
                u.assign_operator_id = None
                u.assign_time = datetime.now()
                u.assign_retain_time = 0
                u.assign_op(None,current_user.id)
        db.session.commit()
        return jsonify(result=True)
    except Exception,e:
        db.session.rollback()
        current_app.logger.error('CHANGE USER TYPE ERROR.%s'%e)
        return jsonify(result=False,error=e.message)


@admin.route('/user/detail/<int:user_id>/<token>')
@admin_required
def user(user_id,token):
    if not des.validate_user_token(token,user_id):
        abort(404)
    user = User.query.options(defer('entries')).get_or_404(user_id)
    logs = User_Assign_Log.query.outerjoin(Operator,User_Assign_Log.assign_operator_id==Operator.id).filter(User_Assign_Log.user_id==user_id).order_by(User_Assign_Log.assign_time)
    return render_template('user/user_authorized.html' if user.is_authorize else 'user/user_unauthorized.html',user=user,assign_logs = logs)


@admin.route('/user/drop/<int:user_id>',methods=['POST'])
@login_required
def drop_user(user_id):
    if request.method=='POST':
        user = User.query.get_or_404(user_id)
        if user.assign_operator_id<>current_user.id:
            return jsonify(result=False,error=u'该客户不归属于你，无法放弃。')
        try:
            user.assign_operator_id = None
            user.assign_retain_time = 0
            user.is_abandon = True
            user.assign_op(None,current_user.id,True)
            db.session.commit()
            current_app.logger.info('DROP_USER|%s|%s|%s|%s'%(user.user_id,user.user_type,current_user.id,datetime.now()))
            return jsonify(result=True)
        except:
            db.session.rollback()
            return jsonify(result=False,error=u'无法放弃该客户')


@admin.route('/user/sms_notify/<int:user_id>',methods=['POST'])
@login_required
def user_sms_notify(user_id):
    if request.method=='POST':
        user = User.query.get_or_404(user_id)
        if user.assign_operator_id<>current_user.id:
            return jsonify(result=False,error=u'非法操作！')

        if user.user_type <> 2:return jsonify(result=False,error=u'客户类型不正确！')
        if user.is_sms:return jsonify(result=False,error=u'该客户已发送短信提醒！')

        try:
            #暂时删除SMS.add_sms(user.mobile_phones,user.sms_message, status=1,user_id=user.user_id,operator_id=current_user.id,remark=u'短信提醒',commit=False)
            #user.is_sms = True
            #db.session.commit()
            return jsonify(result=True)
        except:
            #db.session.rollback()
            return jsonify(result=False,error=u'发送短信失败')


@admin.route('/user/sms_mass',methods=['POST'])
@admin_required
def sms_mass():
    phones = request.form['phones'].split(',')
    message =  request.form['message']
    remark =  request.form['remark']
    p = re.compile(r"((13|14|15|18)\d{9}$)")
    phones = [phone for phone in phones if phone and p.match(phone)]
    if len(phones)==0:return jsonify(result=False,error=u'群发号码为空或错误！')
    group_phones = []
    while True:
        if len(phones)<=200:
            group_phones.append(','.join(phones))
            break
        group_phones.append(','.join(phones[:200]))
        phones = phones[200:]
    #暂时删除20131225
    try:
        for _phones in group_phones:
            SMS.add_sms(_phones,message,status=0,operator_id=current_user.id,remark=remark,commit=False)
        db.session.commit()
        return jsonify(result=True)
    except Exception,e:
        return jsonify(result=False,error=u'群发失败，%s'%e)



@admin.route('/user/sms/list')
@admin_required
def sms_list():
    page = int(request.args.get('page', 1))
    PER_PAGE = 20
    _conditions = []
    status = request.args.get('status','')
    if status<>'': _conditions.append(SMS.status == int(status))

    _start_date = request.args.get('start_date','')
    if _start_date:
        _conditions.append(SMS.created>=_start_date)

    _end_date = request.args.get('end_date','')
    if _end_date:
        _conditions.append(SMS.created<=_end_date)

    if len(_conditions)>0:
        pagination = SMS.query.filter(*_conditions).order_by(desc(SMS.created)).paginate(page, per_page=PER_PAGE)
    else:
        pagination = SMS.query.order_by(desc(SMS.created)).paginate(page, per_page=PER_PAGE)
    return render_template('user/sms_list.html', pagination=pagination)


@admin.route('/user/sms/<int:user_id>')
@login_required
def user_sms(user_id):
    _objs = SMS.query.filter(SMS.user_id==user_id)
    sms_list = []
    for sms in _objs:
        sms_list.append({'message':sms.message,
                         'status':sms.status_name})
    return jsonify(result=sms_list)


@admin.route('/user/sms/approval/<int:sms_id>', methods=['POST'])
@admin_required
def sms_approval(sms_id):
    try:
        sms = SMS.query.get(sms_id)
    except:
        return jsonify(result=False, error=u'记录不存在.')
    if sms.status <> 0: return jsonify(result=False, error=u'非法操作')
    is_confirm = int(request.form['confirm'])
    if is_confirm:
        sms.status = 1
    else:
        db.session.delete(sms)
    db.session.commit()
    return jsonify(result=True)


@admin.route('/user/sms/add/<int:user_id>', methods=['POST'])
@login_required
def add_sms(user_id):
    if request.method == 'POST':
        try:
            #user = User.query.get(user_id)
            #message = request.form['message']
            #暂时删除20131225SMS.add_sms(user.mobile_phones,message,status=0,user_id=user.user_id,operator_id=current_user.id,remark=u'人工',commit=False)
            #db.session.commit()
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('ADD SMS ERROR,%s'%e)
            return jsonify(result=False,error=e.message)


@admin.route('/user/<int:user_id>/dialogs')
@login_required
def user_dialogs(user_id):
    dialogs = User_Dialog.query.join(Operator,Operator.id==User_Dialog.operator_id).filter(User_Dialog.user_id==user_id).order_by(desc(User_Dialog.created))
    _datas = []
    for dialog in dialogs:
        _datas.append({'dialog_id':dialog.id,
                       'solution':dialog.solution,
                       'type_name':DIALOG_TYPES[dialog.type],
                       'content':dialog.content,
                       'record_number':dialog.record_number,
                       'op_name':dialog.operator.nickname,
                       'created':dialog.created.strftime('%Y-%m-%d %H:%M')})
    return jsonify(result = _datas)


@admin.route('/user/<int:user_id>/add_dialog',methods=['POST'])
@login_required
def add_dialog(user_id):
    if request.method == 'POST':
        try:
            content = request.form['content']
            solution = request.form['solution']
            dialog_type = request.form['type']
            record_number = request.form['record_number']
            if not dialog_type:dialog_type=99
            obj = User_Dialog.add_dialog(current_user.id,user_id,solution,int(dialog_type),content,record_number)
            db.session.add(obj)
            db.session.commit()
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('ADD USER DIALOG ERROR,%s'%e)
            return jsonify(result=False,error=e.message)

user_dialogs
def format_phone(phone):
    '''格式化电话号码'''
    if not phone:return ''
    phone = phone.replace('-','')
    if phone.startswith('01') and len(phone) == 12:
        return phone[1:]

    if phone.startswith('028') and len(phone) == 11:
        return phone[3:]
    return phone


def _edit_user(user):
    try:
        username = request.form['name']
        origin = int(request.form['origin'])

        #客户号码校验
        _phones = []
        _user_phones = []
        is_modified_phone = False
        for name in ('user_phone','user_phone2','user_tel','user_tel2'):
            _new_phone = format_phone(request.form[name])
            name = name[5:]
            _old_phone = getattr(user,name)
            if not _old_phone:_old_phone = ''
            if _old_phone<>_new_phone:
                is_modified_phone = True
            if _new_phone and _new_phone not in _phones:_phones.append(_new_phone)
            _user_phones.append((name,_new_phone))

        if is_modified_phone:
            if len(_phones)==0:
                return False,u'客户号码不允许为空！'

            for name,new_phone in _user_phones:
                setattr(user,name,new_phone)

            User_Phone.query.filter(User_Phone.user_id==user.user_id).delete()
            for _phone in _phones:
                db.session.add(User_Phone.add_phone(user.user_id,_phone))


        gender = request.form['gender']
        if not gender:gender = u'保密'

        birthday = request.form['birthday']
        if not birthday:birthday = None
        profession = request.form['profession']

        income = request.form['income']
        if not income:income = 0
        income = int(income)

        ages = request.form['ages']
        if not ages:ages = 0
        ages = int(ages)

        intent_level = request.form['intent_level']

        entries = request.form['entries']
        user.name = username
        user.gender = gender
        user.birthday = birthday
        user.ages = ages
        user.profession = profession
        user.income = income
        user.remark = request.form.get('remark','')
        user.concerns = json.loads(request.form['concerns'])

        user.m1 = request.form['m1']
        user.m2 = request.form['m2']
        user.m3 = request.form['m3']

        expect_time = request.form['expect_time']
        
        is_new = request.form['is_new']
        if not is_new:is_new = 0
        is_new = int(is_new)        
        user.is_new = is_new
        if is_new:
            user.fugou = 0
        else:
            fugou = request.form['fugou']
            if not fugou:fugou = 0
            user.fugou = fugou
        user.disease = request.form['disease']
        #print expect_time
        if expect_time:
            #print datetime.strptime(expect_time,'%Y-%m-%d %H:%M')
            user.expect_time = datetime.strptime(expect_time[:16],'%Y-%m-%d %H:%M')
        else:
            user.expect_time = None

        user.intent_level = intent_level

        user.entries = entries
        user.habits_customs = request.form['habits_customs']
        user.product_intention = request.form['product_intention']
        user.origin = origin
        user.operator_id = current_user.id


        db.session.commit()
        return True,{'user_id':user.user_id,'token':des.user_token(user.user_id)}
    except Exception,e:
        printException()
        db.session.rollback()
        current_app.logger.error('edit user failed, error: %s.' % e)
        return False,e.message


@admin.route('/user/edit/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    if request.method=='POST':
        user = User.query.get_or_404(user_id)
        if not user.is_authorize:abort(404)
        if request.method == 'POST':
            result,desc = _edit_user(user)
            return jsonify(result=result,error=desc)
    abort(404)



# @admin.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
# @admin_required
# def edit_user(user_id):
#     user = User.query.get_or_404(user_id)
#     if not user.is_authorize:abort(404)
#     if request.method == 'POST':
#         result,desc = _edit_user(user)
#         return jsonify(result=result,error=desc)
#     return render_template('user/user_form_new.html',user=user)

@admin.route('/user/complete_expect/<int:user_id>', methods=['POST'])
@login_required
def complete_user_expect(user_id):
    try:
        user = User.query.get(user_id)
        if user.is_authorize:
            user.expect_time = None
            db.session.commit()
            return jsonify(result=True,error='')
        else:
            return jsonify(result=False,error=u'未授权操作！')
    except Exception,e:
        db.session.rollback()
        return jsonify(result=False,error=e.message)

def _add_user():
    try:
        username = request.form['name']
        origin = int(request.form['origin'])

        #客户号码校验
        phones = []
        phone = format_phone(request.form['phone'])
        phone2 = format_phone(request.form['phone2'])
        tel = format_phone(request.form['tel'])
        tel2 = format_phone(request.form['tel2'])
        if phone:phones.append(phone)
        if phone2:phones.append(phone2)
        if tel:phones.append(tel)
        if tel2:phones.append(tel2)
        phones = list(set(phones))
        if len(phones)==0:return False,u'客户电话号码不允许为空'
        for _phone in phones:
            if User_Phone.user_id_by_phone(_phone):
                return False,u'客户资料库已存在号码：%s'%_phone

        gender = request.form['gender']
        if not gender:gender = u'保密'

        birthday = request.form['birthday']
        if not birthday:birthday = None

        ages = request.form['ages']
        if not ages:ages = 0
        ages = int(ages)

        profession = request.form['profession']

        income = request.form['income']
        if not income:income = 0
        income = int(income)

        intent_level = request.form['intent_level']

        entries = request.form['entries']

        #通话记录
        dialog_content = request.form['dialog_content']
        record_number = request.form['record_number']
        if dialog_content:
            dialog_solution = request.form['dialog_solution']
            dialog_type = request.form['dialog_type']
            if not dialog_type:
                dialog_type = 99
            dialog_type = int(dialog_type)

        user = User()
        user.name = username
        user.gender = gender
        user.phone = phone
        user.phone2 = phone2
        user.tel = tel
        user.ages = ages
        user.intent_level = intent_level
        user.tel2 = tel2
        user.user_type = 1
        user.birthday = birthday
        user.profession = profession
        user.income = income

        user.remark = request.form.get('remark','')

        expect_time = request.form['expect_time']
        if expect_time:
            user.expect_time = datetime.strptime(expect_time[:16],'%Y-%m-%d %H:%M')

        user.concerns = json.loads(request.form['concerns'])
        user.m1 = request.form['m1']
        user.m2 = request.form['m2']
        user.m3 = request.form['m3']

        is_new = request.form['is_new']
        if not is_new:is_new = 0
        is_new = int(is_new)        
        user.is_new = is_new
        if is_new:
            user.fugou = 0
        else:
            fugou = request.form['fugou']
            if not fugou:fugou = 0
            user.fugou = fugou
        user.disease = request.form['disease']

        if dialog_content:
            user.dialog_times = 1
            user.last_dialog_time = datetime.now()
            if record_number:
                user.record_time = datetime.now()

        user.entries = entries
        user.habits_customs = request.form['habits_customs']
        user.product_intention = request.form['product_intention']
        user.origin = origin
        user.operator_id = current_user.id
        db.session.add(user)
        db.session.flush()
        user.assign_op(current_user,current_user.id)

        for _phone in phones:
            db.session.add(User_Phone.add_phone(user.user_id,_phone))

        #添加客户地址
        street = request.form.get('street1',None)
        if street:
            address = Address()
            address.user_id = user.user_id
            address.province = request.form.get('province', None)
            address.city = request.form.get('city', None)
            address.district = request.form.get('district', None)
            address.street1 = street
            address.postcode = request.form.get('postcode', None)
            address.ship_to = username
            address.phone = phone
            address.tel = tel
            address.email = request.form.get('email', '')
            db.session.add(address)
            db.session.flush()

        if dialog_content:
            db.session.add(User_Dialog.add_dialog(current_user.id,user.user_id,dialog_solution,dialog_type,dialog_content,record_number))
        db.session.commit()
        return True,{'user_id':user.user_id,'token':des.user_token(user.user_id)}
    except Exception,e:
        db.session.rollback()
        current_app.logger.error('add user failed, error: %s.' % e)
        return False,e.message


@admin.route('/user/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method=='POST':
        result,desc = _add_user()
        return jsonify(result=result,error=desc)
    return render_template('user/user_form_new.html')


@admin.route('/help')
def help():
    return render_template('help.html')

#add john abandon staff approval
@admin.route('/user/giveupuserok',methods=['POST'])
@admin_required
def giveup_user_ok():
    try:
        sel_ids = json.loads(request.form['ids'])
        user_ids = map(lambda s:int(s),sel_ids)
        remarks = request.form['remarks']
        if len(user_ids)==0:return jsonify(result=False,error=u'请先选择要放弃归属的客户！')
        users = User.query.filter(User.user_id.in_(user_ids))
        # for u in users:
        #     if not op.assign_user_type&u.user_type:
        #         return jsonify(result=False,error=u'员工《%s》指派类型和客户《%s》当前类型不匹配！'%(op.nickname,u.name))

        for u in users:
            u.assign_operator_id = None
            u.assign_retain_time = 0
            u.is_abandon = True
            u.assign_op(None,current_user.id,True)

            current_app.logger.info('DROP_USER|%s|%s|%s|%s'%(current_user.id,current_user.id,u.user_id,u.assign_operator_id))

        giveupusers = User_Giveup.query.filter(db.and_(User_Giveup.user_id.in_(user_ids),User_Giveup.status == 0)).all()
        for give in giveupusers:
            give.status = 1
            give.audit_operator_id = current_user.id
            give.audit_time = datetime.now()
            give.remarks = remarks
        #db.session.query(User_Giveup).filter(User_Giveup.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify(result=True)
    except Exception,e:
        printException()
        db.session.rollback()
        current_app.logger.error('DROP_USER ERROR.%s'%e)
        return jsonify(result=False,error=e.message)

@admin.route('/user/giveupuserno',methods=['POST'])
@admin_required
def giveup_user_no():
    try:
        sel_ids = json.loads(request.form['ids'])
        user_ids = map(lambda s:int(s),sel_ids)
        remarks = request.form['remarks']
        if len(user_ids)==0:return jsonify(result=False,error=u'请先选择要放弃归属的客户！')
        users = User.query.filter(User.user_id.in_(user_ids))
        # for u in users:
        #     if not op.assign_user_type&u.user_type:
        #         return jsonify(result=False,error=u'员工《%s》指派类型和客户《%s》当前类型不匹配！'%(op.nickname,u.name))

        for u in users:
            current_app.logger.info('DROP_USERNO|%s|%s|%s|%s'%(current_user.id,current_user.id,u.user_id,u.assign_operator_id))

        giveupusers = User_Giveup.query.filter(db.and_(User_Giveup.user_id.in_(user_ids),User_Giveup.status == 0)).all()
        for give in giveupusers:
            give.status = 2
            give.audit_operator_id = current_user.id
            give.audit_time = datetime.now()
            give.remarks = remarks
        
        db.session.commit()
        return jsonify(result=True)
    except Exception,e:
        printException()
        db.session.rollback()
        current_app.logger.error('DROP_USER ERROR.%s'%e)
        return jsonify(result=False,error=e.message)



@admin.route('/user/giveup_users')
@admin_required
def giveup_users():
    _conditions = user_conditions()
    #仅允许管理本部门员工数据
    #if not current_user.is_admin and current_user.team:
    #    operators = Operator.query.filter(db.and_(Operator.team.like(current_user.team+'%'),Operator.assign_user_type>0))
    #    op_ids = [op.id for op in operators]
    #    _conditions.append(User.assign_operator_id.in_(op_ids))
    #else:
    operators = Operator.query.filter(Operator.assign_user_type>0)

    page = int(request.args.get('page', 1))
    _conditions.append(User_Giveup.status==0)
    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User.join_time)
    if len(_conditions) > 0:
        pagination = User_Giveup.query.filter(db.and_(*_conditions)).join(User,User.user_id==User_Giveup.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    else:
        pagination = User_Giveup.query.filter(db.and_(User_Giveup.status == 0)).join(User,User.user_id==User_Giveup.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/users_fq.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])


#add john 放弃用户
@admin.route('/user/giveup/<int:user_id>',methods=['POST'])
@login_required
def giveup_user(user_id):
    if request.method=='POST':
        user = User.query.get_or_404(user_id)
        reason = request.form['reason']
        if user.assign_operator_id<>current_user.id:
            return jsonify(result=False,error=u'该客户不归属于你，无法放弃。')
        _conditions = []
        _conditions.append(User_Giveup.user_id == user_id)
        _conditions.append(User_Giveup.status == 0)
        giveupuserdata = User_Giveup.query.filter(db.and_(*_conditions)).limit(1)
        giveupusers = []
        for g in giveupuserdata:
            giveupusers.append(g.id)
        if len(giveupusers) > 0:
            return jsonify(result=False,error=u'该客户正在放弃审核中。')
        try:
            giveupuser = User_Giveup();
            giveupuser.user_id = user_id
            giveupuser.operator_id = current_user.id
            giveupuser.reason = reason
            db.session.add(giveupuser)
            db.session.commit()
            current_app.logger.info('GIVEUP_USER|%s|%s|%s|%s'%(user.user_id,user.user_type,current_user.id,datetime.now()))
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            return jsonify(result=False,error=u'无法放弃该客户，%s'%e)

@admin.route('/user/giveup_user_sq')
@admin_required
def giveup_user_sq():
    _conditions = user_conditions()
    operators = Operator.query.filter(Operator.assign_user_type>0)

    page = int(request.args.get('page', 1))
    _conditions.append(User_Giveup.operator_id == current_user.id)
    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User_Giveup.created)
    if len(_conditions) > 0:
        pagination = User_Giveup.query.filter(db.and_(*_conditions)).join(User,User.user_id==User_Giveup.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    else:
        pagination = User_Giveup.query.filter(db.and_(User_Giveup.status == 0)).join(User,User.user_id==User_Giveup.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/giveup_user_sq.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])

@admin.route('/user/giveup_user_audit')
@admin_required
def giveup_user_audit():
    _conditions = user_conditions()
    operators = Operator.query.filter(Operator.assign_user_type>0)

    page = int(request.args.get('page', 1))
    _conditions.append(User_Giveup.audit_operator_id == current_user.id)
    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User_Giveup.created)
    if len(_conditions) > 0:
        pagination = User_Giveup.query.filter(db.and_(*_conditions)).join(User,User.user_id==User_Giveup.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    else:
        pagination = User_Giveup.query.filter(db.and_(User_Giveup.status == 0)).join(User,User.user_id==User_Giveup.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/giveup_user_sq.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])


#导出用
@admin.route('/user/johndc')
@login_required
def john_users():
    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User.join_time)
    _conditions = user_conditions()
    #_conditions.append(User.last_dialog_time>='2013-09-01')
    _conditions.append(User.last_dialog_time<'2013-8-01')   
    _conditions.append(User.order_fee == 0)
    pagination2 = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(db.and_(*_conditions)).filter(db.and_(User.user_type == 1)).order_by(order_by)
    #return 'ok'
    return render_template('user/userjohn.html',
                           #pagination=pagination,
                           pagination2=pagination2,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])

@admin.route('/securitycode/search', methods=['GET', 'POST'])
@admin_required
def securitycodes():
    code = request.args.get('code', None)
    username = request.args.get('username', None)
    tel = request.args.get('tel', None)
    province = request.args.get('province', None)
    city = request.args.get('city', None)
    district = request.args.get('district', None)
    street = request.args.get('street', None)
    sc = None    
    scc = None
    if code:        
        sc = Security_Code.query.filter(db.and_(Security_Code.code == code)).first()
        if sc:
            scc = Security_Code_Log.query.filter(db.and_(Security_Code_Log.code == code)).first()
        if not scc:
            scl = Security_Code_Log()
            scl.operator_id = current_user.id
            scl.code = code
    #        scl.username = username
    #        scl.tel = tel
    #        scl.province = province
    #        scl.city = city
    #        scl.district = district
    #        scl.street = street
            scl.ip = request.remote_addr
            db.session.add(scl)
            db.session.commit()
    return render_template('securitycode/search.html', scc=scc,sc=sc,code=code)
@admin.route('/securitycode/searchlog', methods=['GET', 'POST'])
@admin_required
def securitycodelog():
    _conditions = []
    code = request.args.get('code', None)
    if code:
        _conditions.append('`security_code_log`.`code` ="'+code+'"')
    username = request.args.get('username', None)
    if username:
        _conditions.append('`security_code_log`.`username` ="'+username+'"')
    tel = request.args.get('tel', None)
    if tel:
        _conditions.append('`security_code_log`.`tel` ="'+tel+'"')
    province = request.args.get('province', None)
    if province:
       _conditions.append('`security_code_log`.`province` ="'+province+'"')
    city = request.args.get('city', None)
    if city:
       _conditions.append('`security_code_log`.`city` ="'+city+'"')

    district = request.args.get('district', None)
    if district:
       _conditions.append('`security_code_log`.`district` ="'+district+'"')
    street = request.args.get('street', None)
    if street:
       _conditions.append('`security_code_log`.`street` ="'+street+'"')
    page = int(request.args.get('page', 1))
    pagination = Security_Code_Log.query.filter(*_conditions).paginate(page, per_page=20)

    return render_template('securitycode/searchlog.html', pagination=pagination)

@admin.route('/order/lhyd_yz', methods=['GET', 'POST'])
@admin_required
def order_lhyd_yz():
    order_id = request.args.get('order_id', None)
    express_number = request.args.get('express_number', None)
    page = int(request.args.get('page', 1))
    if order_id:
        try:        
            lhyd = Order_LHYD_Postal()
            lhyd.order_id = int(order_id)
            lhyd.express_number = express_number
            db.session.add(lhyd)
            db.session.commit()    
        except Exception, e:
                db.session.rollback()
                restr = 'error: %s.' % e

    return render_template('order/order_lhyd_yz.html')

@admin.route('/category/manage', methods=['POST', 'GET'])
@admin_required
def categorys():
    form = CategoryForm()
    if form.validate_on_submit():
        kc = Knowledge_Category()
        form.populate_obj(kc)
        db.session.add(kc)
        db.session.commit()
        flash(u'类别《%s》已添加！' % form.name.data)
        return redirect(request.path)
    items = Knowledge_Category.query.filter()
    return render_template('knowledge/category.html', form=form, items=items)


@admin.route('/category/del/<int:item_id>', methods=['POST'])
@admin_required
def del_category(item_id):
    try:
        item = Knowledge_Category.query.get(item_id)
    except:
        return jsonify(result=False, error=u'类别不存在')

    item.status = False
    db.session.commit()
    return jsonify(result=True)

@admin.route('/knowledge/manage')
@admin_required
def manage_knowledge():
    page = int(request.args.get('page', 1))
    pagination = Knowledge.query.order_by(desc(Knowledge.created)).paginate(page, per_page=20)
    return render_template('knowledge/knowledge.html', pagination=pagination)

@admin.route('/knowledge/search/')
@admin_required
def search_knowledge():
    q = request.args.get('q','none')
    if q:
        pass
    else:
        categorylist = Knowledge_Category.query.filter()
        for c in categorylist:
            bb = Knowledge.query.filter(Knowledge.category_id == c.id)
        print categorylist
    news_list = Knowledge.query.join(Knowledge_Category,Knowledge_Category.id==Knowledge.category_id).filter('knowledge.title like \'%%'+q+'%%\' or knowledge_category.name =\''+q+'\'').order_by(desc(Knowledge.created))
    print news_list
    return render_template('knowledge/search.html', news_list=news_list)



@admin.route('/knowledge/edit/<int:knowledge_id>', methods=['POST', 'GET'])
@admin_required
def edit_knowledge(knowledge_id):
    knowledge = Knowledge.query.get_or_404(knowledge_id)
    form = KnowledgeForm(obj=Knowledge)
    items = Knowledge_Category.query.filter()
    if form.validate_on_submit():
        form.populate_obj(knowledge)
        knowledge.category_id = int(request.form['category_id'])
        db.session.commit()
        return redirect(url_for('admin.manage_knowledge'))
    return render_template('knowledge/knowledge_form.html', items=items,knowledge=knowledge,form=form, is_edit=True)


@admin.route('/knowledge/add', methods=['GET', 'POST'])
@admin_required
def add_knowledge():
    form = KnowledgeForm()
    items = Knowledge_Category.query.filter()
    if form.validate_on_submit():
        knowledge = Knowledge()
        form.populate_obj(knowledge)
        knowledge.category_id = int(request.form['category_id'])
        knowledge.operator_id = current_user.id
        db.session.add(knowledge)
        db.session.commit()
        return redirect(url_for('admin.manage_knowledge'))
    return render_template('knowledge/knowledge_form.html', items=items,form=form)

@admin.route('/knowledge/get/<int:id>', methods=['GET'])
@admin_required
def get_knowledge(id):
    knowledge = Knowledge()
    try:
        knowledge = Knowledge.query.get_or_404(id)
    except:
        return jsonify(result=False, error=u'知识不存在'+str(id))
    
    return jsonify(result=True,knowledge=knowledge.content)


@admin.route('/knowledge/delete/<int:id>', methods=['POST'])
@admin_required
def del_knowledge(id):
    try:
        knowledge = Knowledge.query.get(id)
    except:
        return jsonify(result=False, error=u'知识不存在')
    db.session.delete(knowledge)
    db.session.commit()
    return jsonify(result=True)

#end john
@admin.route('/user/dropgiveup_user',methods=['GET'])
@login_required
def dropgiveup_user():
    pagination = db.session.execute('drop table user_giveup')
    db.session.commit()
    return 'ok'

@admin.route('/john/changeorder',methods=['GET'])
@login_required
def changeorder():
    restr = 'ok'
    try:
        #status状态 assign_operator_id下一步ID
        db.session.execute('update `order` set status=5 where order_id=13092900081')
        db.session.execute('insert into order_log values (null,13092900081,1,now(),5,\'管理员返回已发货\',\'127.0.0.1\')')
        db.session.commit()
    except Exception, e:
        db.session.rollback()
        restr = 'error: %s.' % e
    return restr
@admin.route('/john/dcstockin')
@login_required
def john_dcstockin():
    _conditions = []    
    _conditions.append(Stock_In.created>='2013-09-01')    
    _conditions.append(Stock_In.created<'2013-10-01')
    pagination = Stock_In.query.join(Sku,Sku.id==Stock_In.sku_id).filter(*_conditions).order_by(desc(Stock_In.created))
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('stock/dc.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])

#导出4到8月 拒收退货确认9
@admin.route('/john/dcz20131022')
@login_required
def john_dcz20131022():
    _conditions = []    
    _conditions.append(Order.created>='2013-4-01')    
    _conditions.append(Order.created<'2013-9-01')
    _conditions.append(Order.status == 9)
    pagination = Order.query.join(Order_Item,Order_Item.order_id==Order.order_id).filter(*_conditions).order_by(desc(Order.created))
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcz20131022.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])

#导出9到10月 销售退货102
@admin.route('/john/dcz20131104')
@login_required
def john_dcz20131104():
    #_conditions = []   
    _conditions = ['`order`.status IN (102,104)','`end_time` IS NOT NULL'] 
    _conditions.append(Order.end_time>='2013-9-01')    
    _conditions.append(Order.end_time<'2013-11-01')
    pagination = Order.query.filter(*_conditions).order_by(desc(Order.created))
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcz20131104.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])


#导出11月前公共库TQ来源的数据
@admin.route('/john/dcd20131111')
@login_required
def john_dcd20131111():
    #_conditions = []   
    _conditions = [User.user_type==1]     
    _conditions.append(User.assign_operator_id == None)
    _conditions.append(User.dialog_times>1)
    _conditions.append(User.dialog_times<6)
    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])
#导出所有会员客户的数据
@admin.route('/john/dcx20131113')
@login_required
def john_dcd20131113():
    #_conditions = []   
    _conditions = [User.user_type==2]     
    _conditions.append(User.assign_operator_id == None)
    _conditions.append(User.dialog_times<2)
    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])
#会员客户数量统计详细
@admin.route('/sale/user_report_list')
@admin_required
def sale_report_user_list():
    _conditions = user_conditions()
    list_date=request.args.get('list_date')
    list_type=int(request.args.get('list_type', 0))
    us = User_Statistics.query.filter(User_Statistics.tjdate==list_date).first()
    if us:
        hg_user_list= us.hg_user_list
        cm_user_list= us.cm_user_list
        if us.hg_user_list:
            if list_type == 1:
                _conditions.append('user.user_id in ('+hg_user_list+')')
            else:
                if us.cm_user_list:
                    _conditions.append('user.user_id in ('+cm_user_list+')')
                else:
                    _conditions.append('user.user_id in (0)')
        else:
            _conditions.append('user.user_id in (0)')
    else:
        _conditions.append('user.user_id in (0)')
    page = int(request.args.get('page', 1))
    is_order,order_by = user_order_by()
    if not is_order:order_by = asc(User.is_assigned)
    pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(db.and_(*_conditions)).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/user_list.html',
                           pagination=pagination,
                           list_date=list_date,
                           list_type=list_type,
                           show_label = True,
                           operators=Operator.query.filter(Operator.assign_user_type==2),
                           show_queries=['list_date','admin','op','username','phone','user_origin'])
#会员客户数量统计详细
@admin.route('/sale/user_list')
@admin_required
def sale_user_list():
    _conditions = user_conditions()
    list_type=int(request.args.get('list_type', 0))
    if list_type == 1:
        _conditions.append('user.user_id in (select (u.user_id) from `user` u join `order` o on o.user_id=u.user_id where u.batch_id IS NULL AND u.user_type=2 and datediff(now(),o.created)<=90)')
    else:
        _conditions.append('user.user_id in (select (u.user_id) from `user` u join `order` o on o.user_id=u.user_id where u.batch_id IS NULL AND u.user_type=2 and u.user_id not in (select user_id from `order` where datediff(now(),created)<=90))')
    page = int(request.args.get('page', 1))
    is_order,order_by = user_order_by()
    if not is_order:order_by = asc(User.is_assigned)
    pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(db.and_(*_conditions)).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/user_list.html',
                           pagination=pagination,
                           list_type=list_type,
                           show_label = True,
                           operators=Operator.query.filter(Operator.assign_user_type==2),
                           show_queries=['admin','op','username','phone','user_origin'])

#导出11月前公共库TQ来源的数据
@admin.route('/john/dcd20131205')
@login_required
def john_dcd20131205():
    #_conditions = []   
    _conditions = [User.user_type==1]     
    _conditions.append(User.assign_operator_id == None)
    _conditions.append(User.dialog_times>=6)
    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#面,胸,子宫,胸腰,后面的具体文字内容
@admin.route('/user/entries')
@admin_required
def entries():
    #userm = User.query.filter('entries like \'%A10%\'')
    #a = len(list(userm))
    #userx = User.query.filter('entries like \'%B11%\' and user_id<>30326')#胸
    #userzg = User.query.filter('entries like \'%B07%\' and user_id<>30326')#子宫
    userxy = User.query.filter('entries like \'%C06%\' and user_id<>30326')#胸腰
    return render_template('user/user_entries.html',userxy=userxy)
#导出11月前公共库TQ来源的数据
@admin.route('/john/dcd20131219')
@login_required
def john_dcd20131219():
    #_conditions = []   
    _conditions = ['(batch_id <> \'20130718\' or batch_id is null)']     
    _conditions.append(User.assign_operator_id == 89)
    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#导出芪枣健胃茶的数据
@admin.route('/john/dcd20140106')
@login_required
def john_dcd20140106():
    _conditions = []   
    #_conditions = ['user.product_intention=1 and user.dialog_times>5']     
    _conditions.append(User.assign_operator_id == None)
    _conditions.append(User.product_intention == 1)
    _conditions.append(User.dialog_times > 5)
    _conditions.append(User.user_type == 1)

    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#导出芪枣健胃茶的数据
@admin.route('/john/dcd20140221')
@login_required
def john_dcd20140221():
    _conditions = []   
    _conditions = ['(user.product_intention=1 or user.remark like \'\%芪\%\')']     
    _conditions.append(User.user_type == 2)
    _conditions.append('(operator.team in (\'C1\',\'C2\') AND id<>40)')

    pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#导出气血和的数据
@admin.route('/john/dcd20140304')
@login_required
def john_dcd20140304():
    _conditions = []   
    _conditions = ['(user.product_intention=0 or user.remark like \'\%气血和\%\')']     
    _conditions.append(User.user_type == 2)
    _conditions.append('(operator.team in (\'C1\',\'C2\') AND id<>40)')

    pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#导出会员库的数据
@admin.route('/john/dcd20140311')
@login_required
def john_dcd20140311():
    _conditions = []   
    _conditions = ['(user.product_intention<>1 or user.remark like \'\%芪枣\%\')']     
    _conditions.append(User.user_type == 2)
    #_conditions.append('(operator.team in (\'C1\',\'C2\') AND id<>40)')

    pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@admin.route('/order/fast_delivery_detal',methods=['GET'])
@admin_required
def order_fast_delivery_detal():
    _sql1 = '''SELECT `order`.store_id,sku.name,sum(order_item.quantity) FROM `order_item` join sku on sku.id=order_item.sku_id
join `order` on `order`.order_id=order_item.order_id
 WHERE order_item.order_id in (select order_id from `order` where status=4 and store_id='''+str(current_user.store_id)+''') group by `order`.store_id,sku.name'''
    if current_user.is_admin:
        _sql1 = '''SELECT `order`.store_id,sku.name,sum(order_item.quantity) FROM `order_item` join sku on sku.id=order_item.sku_id
         join `order` on `order`.order_id=order_item.order_id
         WHERE order_item.order_id in (select order_id from `order` where status=4) group by `order`.store_id,sku.name'''
        
    #return _sql2
    totaljx = []#所有订单总额
    #totalss = []#所有订单数
    
    #return _sql1
    rows2 = db.session.execute(_sql1)
    _sql2 = 'select count(order_id) from `order` where status=4 and store_id='+str(current_user.store_id)
    if current_user.is_admin:
        _sql2 = 'select count(order_id) from `order` where status=4'
    totalss = db.session.execute(_sql2)
    return render_template('order/fast_delivery_detal.html',totaljx=totaljx,totalss=totalss,rows2=rows2)

@admin.route('/order/retransmission',methods=['GET'])
@admin_required
def order_retransmission():
    _sql1 = '''select * from (select count(order_id) as cc,order_id,operate_time from order_log where to_status=5 group by order_id,operate_time ) aa where cc>1 order by order_id desc; '''+str(current_user.store_id)+''') group by `order`.store_id,sku.name'''
      
    #return _sql2
    totaljx = []#所有订单总额
    #totalss = []#所有订单数
    
    #return _sql1
    rows2 = db.session.execute(_sql1)
    #totalss = db.session.execute(_sql2)
    return render_template('order/retransmission.html',totaljx=totaljx,rows2=rows2)


@admin.route('/order/hasarrived',methods=['POST', 'GET'])
@admin_required
def hasarrived():
    if request.method == 'POST':
        op = request.form['op']
        if op == '1':
            orderids = request.form['orders']
            orders = orderids.split(',')
            orders1 = orders
#            p = re.compile(r"(\d{11}$)")
#            orders = [order for order in orders if order and p.match(order)]
#            if len(orders)==0 or len(orders1)>len(orders):return jsonify(result=False,error=u'订单号格式错误！')
         
            page = int(request.args.get('page', 1))
            orders = Order.query.filter('status=6 and express_number in (\''+orderids.replace(',','\',\'')+'\')').paginate(page, per_page=user_per_page())
            print orders
            if orders.total<len(orders1):
                return jsonify(result=False,error='订单号状态错误或重复！')
            try:
                for order in orders.items:
                    result,desc = _manage_order(order,60,u'一键物流对帐')
                    if result is not True:
                        raise Exception(u'处理订单《%s》发生错误：%s'%(order.order_id,desc))
                return jsonify(result=True)
            except Exception,e:
                current_app.logger.error('FAST Reconciliation ERROR.%s'%e)
                return jsonify(result=False,error=e.message)
        else:
            orderids = request.form['orders']
            #print orderids
            orders = orderids.split('\r\n')
            orders1 = orders
#            p = re.compile(r"(\d{11}$)")
#            orders = [order for order in orders if order and p.match(order)]
            #print len(orders1)>len(orders)
            msg = ''
            #if len(orders)==0 or len(orders1)>len(orders):msg = '订单号格式错误！'#return jsonify(result=False,error=u'订单号为空或错误！')

            if msg:
                return render_template('order/hasarrived.html',orderids=orderids,msg=msg)  
            msg = ''
            page = int(request.args.get('page', 1))
            orders = Order.query.filter('status=6 and express_number in (\''+orderids.replace('\r\n','\',\'')+'\')').paginate(page, per_page=user_per_page())
            print orders
            if orders.total<len(orders1):
                msg = '订单号状态错误或重复！'
            return render_template('order/hasarrived.html',orderids=orderids,msg=msg,orders=orders)    
    else:
        page = int(request.args.get('page', 1))
        orders = Order.query.filter('1=2').paginate(page, per_page=user_per_page())
        return render_template('order/hasarrived.html',orders=orders)

@admin.route('/order/caiwuqr',methods=['POST', 'GET'])
@admin_required
def caiwuqr():
    if request.method == 'POST':
        print 'ok'
        op = request.form['op']
        if op == '1':
            orderids = request.form['orders']
            orders = orderids.split(',')
            orders1 = orders
            #p = re.compile(r"(\d{11}$)")
            #orders = [order for order in orders if order and p.match(order)]
            #if len(orders)==0 or len(orders1)>len(orders):return jsonify(result=False,error=u'订单号格式错误！')
         
            page = int(request.args.get('page', 1))
#            print orderids
#            print 'status=60 and express_number in (\''+orderids.replace(',','\',\'')+'\')'
#            return 'ok'
            orders = Order.query.filter('status=60 and express_number in (\''+orderids.replace(',','\',\'')+'\')').paginate(page, per_page=user_per_page())
            print orders.total
            if orders.total<len(orders1):
                return jsonify(result=False,error='订单号状态错误或重复！')
            try:
                for order in orders.items:
                    result,desc = _manage_order(order,100,u'一键财务确认')
                    if result is not True:
                        raise Exception(u'处理订单《%s》发生错误：%s'%(order.order_id,desc))
                return jsonify(result=True)
            except Exception,e:
                current_app.logger.error('FAST Reconciliation ERROR.%s'%e)
                return jsonify(result=False,error=e.message)
        else:
            orderids = request.form['orders']
            #print orderids
            orders = orderids.split('\r\n')
            orders1 = orders
            #p = re.compile(r"(\d{11}$)")
            #orders = [order for order in orders if order and p.match(order)]
            #print len(orders1)>len(orders)
            msg = ''
            #if len(orders)==0 or len(orders1)>len(orders):msg = '订单号格式错误！'#return jsonify(result=False,error=u'订单号为空或错误！')

            if msg:
                return render_template('order/caiwuqr.html',orderids=orderids,msg=msg)  
            msg = ''
            page = int(request.args.get('page', 1))
            orders = Order.query.filter('status=60 and express_number in (\''+orderids.replace('\r\n','\',\'')+'\')').paginate(page, per_page=user_per_page())
            print orders.total
            if orders.total<len(orders1):
                msg = '订单号状态错误或重复！'
            return render_template('order/caiwuqr.html',orderids=orderids,msg=msg,orders=orders)    
    else:
        page = int(request.args.get('page', 1))
        orders = Order.query.filter('1=2').paginate(page, per_page=user_per_page())
        return render_template('order/caiwuqr.html',orders=orders)

#add john 添加代金卷
@admin.route('/user/voucher_add/<int:user_id>',methods=['POST'])
@login_required
def voucher_add(user_id):
    if request.method=='POST':
        user = User.query.get_or_404(user_id)
        remark = request.form['remark']
        price = request.form['price']
        if user.assign_operator_id<>current_user.id:
            return jsonify(result=False,error=u'该客户不归属于你，无法添加代金卷。')
        _conditions = []
        _conditions.append(User_Voucher.user_id == user_id)
        voucheruserdata = User_Voucher.query.filter(db.and_(*_conditions)).limit(1)
        voucherusers = []
        for g in voucheruserdata:
            voucherusers.append(g.id)
        try:
            voucheruser = User_Voucher();
            voucheruser.user_id = user_id
            voucheruser.operator_id = current_user.id
            voucheruser.remark = remark
            voucheruser.price = price
            if len(voucherusers) > 0:
                if remark=='':
                    return jsonify(result=False,error=u'原因为空,请填写原因!')
                voucheruser.status = False
            else:
                voucheruser.status = True
            db.session.add(voucheruser)
            db.session.commit()
            current_app.logger.info('VOUCHER_USER|%s|%s|%s|%s'%(user.user_id,voucheruser.id,current_user.id,datetime.now()))
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            return jsonify(result=False,error=u'无法添加代金卷，%s'%e)
#add john 获取代金卷
@admin.route('/user/voucher_get',methods=['POST'])
@login_required
def voucher_get():
    if request.method=='POST':
#        user_id = request.form['user_id']
#        user = User.query.get_or_404(user_id)
#        _conditions = []
#        _conditions.append(User_Voucher.user_id == user_id)    
#        _conditions.append(User_Voucher.status == True)
#        order_id = request.form['order_id']
#        if order_id:
#            _conditions.append(db.or_(User_Voucher.order_id == None,User_Voucher.order_id == int(order_id)))
#        else:
#            _conditions.append(User_Voucher.order_id == None)
#        voucheruser = User_Voucher.query.filter(db.and_(*_conditions))
        _uservoucher = []
#        for vr in voucheruser:
#            _uservoucher.append({'id': vr.id,
#                               'price': vr.price,
#                               'created': vr.created.strftime('%Y-%m-%d')
#                                })

        return jsonify(uservoucher=_uservoucher)
#地面相关
@admin.route('/getdmuser', methods=['GET', 'POST'])
def getdmuser():
    html = StringIO()
    url = r'%sgetuser'%DMURL
    print url
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.SSL_VERIFYHOST, False)
    c.setopt(pycurl.SSL_VERIFYPEER, False)
    c.setopt(pycurl.WRITEFUNCTION, html.write)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.perform()
    
    ll = str(html.getvalue())
    users = json.loads(ll)
    for u in users:
        user = User()
        p = User_Phone.query.filter(db.or_(User_Phone.phone == u['phone'],User_Phone.phone == u['phone2'])).first()
        if p:
            user = User.query.get_or_404(p.user_id)
            user.operator_id = 1
            user.assign_operator_id = 1
            purchases = u['name']+u'于'+u['gmdate']+u' 在 '+u['gmaddress']+u' 购买了大盒'+str(u['gmbigcount'])+u'盒，小盒'+str(u['gmsmallcount'])+u'盒,备注：'+u['remark']+u',电话：'+u['phone']+','+u['phone2']+u',年龄：'+str(u['ages'])+u',性别：'+u['gender']
            user.purchases = purchases
            user.qxhdm_user_id = u['id']

            db.session.add(user)

        else:            
            user.operator_id = 1
            user.assign_operator_id = 1
            user.name = u['name']
            user.phone = u['phone']
            user.phone2 = u['phone2']
            user.gender = u['gender']
            user.ages = u['ages']
            user.is_new = u['is_new']
            user.disease = u['disease']
            user.fugou = u['fugou']
            user.remark = u['remark']
            purchases = u['gmdate']+u' 在 '+u['gmaddress']+u' 购买了大盒'+str(u['gmbigcount'])+u'盒，小盒'+str(u['gmsmallcount'])+u'盒'
            user.purchases = purchases
            user.qxhdm_user_id = u['id']

            db.session.add(user)
            db.session.flush()

        url = r'%supdateuser?id=%s&user_id=%s'%(DMURL,u['id'],user.user_id)
        print url
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.SSL_VERIFYHOST, False)
        c.setopt(pycurl.SSL_VERIFYPEER, False)
        c.setopt(pycurl.WRITEFUNCTION, html.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.perform()

        db.session.commit()
    return ll

@admin.route('/dm/status',methods=['POST'])
@login_required
def dmyx():
    if request.method=='POST':
        try:
            user_id = request.form['user_id']
            status = request.form['status']
            user = User.query.get_or_404(user_id)
            user.is_valid = status
            db.session.add(user)
            db.session.commit()
            
            html = StringIO()
            url = r'%supdateyx?id=%s&is_valid=%s'%(DMURL,user.qxhdm_user_id,user.is_valid)
            print url
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.SSL_VERIFYHOST, False)
            c.setopt(pycurl.SSL_VERIFYPEER, False)
            c.setopt(pycurl.WRITEFUNCTION, html.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.perform()


            return jsonify(result=True)
        except:
            db.session.rollback()
            return jsonify(result=False, error=u'判断错误')

@admin.route('/user/qxhdm')
@admin_required
def qxhdm_users():
    #仅允许管理本部门员工数据
    if not current_user.is_admin and current_user.team:
        operators = Operator.query.filter(db.and_(Operator.team.like(current_user.team+'%'),Operator.assign_user_type>0,Operator.status<>9))
    else:
        operators = Operator.query.filter(Operator.assign_user_type>0,Operator.status<>9)

    user_type = 0    
    _conditions = []
    _conditions.append(User.operator_id ==1 )
    _conditions.append(User.assign_operator_id == None)
    _conditions.append(User.qxhdm_user_id > 0)
    page = int(request.args.get('page', 1))
    is_order,order_by = user_order_by()
    if not is_order:order_by = asc(User.is_assigned)
    pagination = User.query.outerjoin(Operator,User.assign_operator_id==Operator.id).filter(db.and_(*_conditions)).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/users_dm.html',
                           pagination=pagination,
                           show_label = True if user_type==1 else False,
                           operators=operators,
                           show_queries=['admin'])

#重入库
@admin.route('/order/repeatinsku',methods=['GET'])
@admin_required
def order_repeatinsku():
    _sql1 = '''select * from (select count(order_id) as cc,order_id,DATE_FORMAT(operate_time,'%Y-%m-%d %H:%i') from order_log where to_status=104 group by order_id,DATE_FORMAT(operate_time,'%Y-%m-%d %H:%i') ) aa where cc>1 order by order_id desc; '''+str(current_user.store_id)+''') group by `order`.store_id,sku.name'''
      
    #return _sql2
    totaljx = []#所有订单总额
    #totalss = []#所有订单数
    
    #return _sql1
    rows2 = db.session.execute(_sql1)
    #totalss = db.session.execute(_sql2)
    return render_template('order/repeatinsku.html',totaljx=totaljx,rows2=rows2)


@admin.route('/user/voucheradd',methods=['POST', 'GET'])
@admin_required
def voucheradd():
    if request.method == 'POST':
        print 'ok'
        orderids = request.form['orders']
        remark = request.form.get('remark', None)
        #print orderids
        phones = orderids.split('\r\n')
        try:
            for phone in phones:
                user_id = User_Phone.user_id_by_phone(phone)
                print phone
                if user_id:
                    voucheruser = User_Voucher();
                    voucheruser.user_id = user_id
                    voucheruser.operator_id = current_user.id
                    voucheruser.remark = remark
                    voucheruser.price = 20
                    voucheruser.status = True
                    db.session.add(voucheruser)
                    db.session.commit()
                    current_app.logger.info('VOUCHER_USER|%s|%s|%s|%s'%(user_id,voucheruser.id,current_user.id,datetime.now()))
        
        except Exception,e:
            db.session.rollback()
            return jsonify(result=False,error=u'无法添加代金卷，%s'%e)
        return jsonify(result=True)
    else:
        page = int(request.args.get('page', 1))
        orders = Order.query.filter('1=2').paginate(page, per_page=user_per_page())
        return render_template('user/voucheradd.html',orders=orders)

@admin.route('/user/dmyp/<int:user_id>', methods=['POST'])
@login_required
def add_dmyp(user_id):
    if request.method == 'POST':
        try:
            user = User.query.get(user_id)
            orderyf = QXHDM_Orderyf()
            orderyf.user_id = user.user_id
            orderyf.dm_user_id = 0
            if user.qxhdm_user_id:
                orderyf.dm_user_id = user.qxhdm_user_id

            bigcount = int(request.form['bigcount'])
            mediumcount = int(request.form['mediumcount'])
            smallcount = int(request.form['smallcount'])
            orderyf.bigcount = bigcount
            orderyf.mediumcount = mediumcount
            orderyf.smallcount = smallcount

            db.session.add(orderyf)
            user.lastfugou_time = datetime.now().strftime('%Y-%m-%d')
            user.fugou_bigcount += bigcount
            user.fugou_mediumcount += mediumcount
            user.fugou_smallcount += smallcount
            db.session.commit()
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('ADD SMS ERROR,%s'%e)
            return jsonify(result=False,error=e.message)
#服务推荐复购
@admin.route('/user/fwtjfg/<int:user_id>', methods=['POST'])
@login_required
def user_fwtjfg(user_id):
    if request.method == 'POST':
        try:
            user = User.query.get(user_id)
            #print 'ok.....................'
            orderyf = User_tjfg()
            orderyf.user_id = user.user_id
            orderyf.dm_user_id = 0
            if user.qxhdm_user_id:
                orderyf.dm_user_id = user.qxhdm_user_id
            bigcount = int(request.form['bigcount'])
            mediumcount = int(request.form['mediumcount'])
            smallcount = int(request.form['smallcount'])
            orderyf.bigcount = bigcount
            orderyf.mediumcount = mediumcount
            orderyf.smallcount = smallcount

            db.session.add(orderyf)
#            user.lastfugou_time = datetime.now().strftime('%Y-%m-%d')
#            user.fugou_bigcount += bigcount
#            user.fugou_mediumcount += mediumcount
#            user.fugou_smallcount += smallcount
            db.session.commit()
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('ADD USERTJFG ERROR,%s'%e)
            return jsonify(result=False,error=e.message)

@admin.route('/user/voucher/<int:user_id>')
@login_required
def user_voucher(user_id):
    _objs = User_Voucher.query.filter(User_Voucher.user_id==user_id)
    sms_list = []
    for sms in _objs:
        sms_list.append({'message':str(sms.created),
                         'status':sms.remark})
    return jsonify(result=sms_list)

@admin.route('/user/orderyf/<int:user_id>')
@login_required
def user_orderyf(user_id):
    _objs = QXHDM_Orderyf.query.filter(QXHDM_Orderyf.user_id==user_id)
    sms_list = []
    for sms in _objs:
        sms_list.append({'message':str(sms.created),
                         'bigcount':sms.bigcount,
                         'mediumcount':sms.mediumcount,
                         'smallcount':sms.smallcount

})
    return jsonify(result=sms_list)

@admin.route('/order/getuserinfobyeid',methods=['POST', 'GET'])
@admin_required
def getuserinfobyeid():
    if request.method == 'POST':
        print 'ok'
        eid = request.form['eid']
        if eid:
            order = Order.query.filter(Order.express_number == eid).first()
            if order:
                return jsonify(result=True,order_id=order.order_id,express_number=order.express_number,name=order.publisher.nickname)
        return jsonify(result=False,error=u'查询失败')
    else:
        return render_template('order/getuserinfobyeid.html')


@admin.route('/order/securitycode_khbmcx',methods=['POST', 'GET'])
@admin_required
def securitycode_khbmcx():
    if request.method == 'POST':
        orderids = request.form['orders']
        #print orderids
        orders = orderids.split('\r\n')
        orders1 = orders
        orders = Security_Codekh.query.filter('code in (\''+orderids.replace('\r\n','\',\'')+'\')').all()
        print orders
        return render_template('securitycode/kxbmcx.html',orderids=orderids,orders=orders)    
    else:
        orders = Order.query.filter('1=2').all()
        return render_template('securitycode/kxbmcx.html',orders=orders)

@admin.route('/user/khsldj/<int:user_id>', methods=['POST'])
@login_required
def khsldj(user_id):
    if request.method == 'POST':
        try:
            user = User.query.get(user_id)
            qxhkjdj = QXHKHDJ()
            qxhkjdj.user_id = user.user_id
            qxhcode = request.form['qxhcode']
            qxhcodes = qxhcode.split(',')
            page = int(request.args.get('page', 1))
            print qxhcode
            print qxhcode.replace(',','\',\'')
            print 'qxhkjdj_id is null and code in (\''+qxhcode.replace('\r\n','\',\'')+'\')'
            codes = Security_Codekh.query.filter('qxhkjdj_id is null and code in (\''+qxhcode.replace(',','\',\'')+'\')').paginate(page, per_page=user_per_page())
            print codes.total
            print len(qxhcodes)
            if codes.total<len(qxhcodes):
                return jsonify(result=False,error='空盒编码错误或已登记！')
            giftname = request.form['giftname']
            giftcount = request.form['giftcount']
            province = request.form['province']
            city = request.form['city']
            district = request.form['district']
            pharmacyaddress = request.form['pharmacyaddress']
            qxhkjdj.qxhcode = qxhcode
            qxhkjdj.giftname = giftname
            qxhkjdj.giftcount = giftcount
            qxhkjdj.province = province
            qxhkjdj.city = city
            qxhkjdj.district = district
            qxhkjdj.pharmacyaddress = pharmacyaddress
            _date = datetime.now().strftime('%Y-%m-%d')
            qxhkjdj.date = _date

            db.session.add(qxhkjdj)
            db.session.flush()
            for c in codes.items:
                c.qxhkjdj_id = qxhkjdj.id
                db.session.add(c)
            db.session.commit()
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('ADD QXHKHHLDJ ERROR,%s'%e)
            return jsonify(result=False,error=e.message)


@admin.route('/user/showkhsldj/<int:user_id>')
@login_required
def user_show_khsldj(user_id):
    _objs = QXHKHDJ.query.filter(QXHKHDJ.user_id==user_id)
    sms_list = []
    for sms in _objs:
        sms_list.append({'qxhcode':str(sms.qxhcode),
                         'giftname':sms.giftname,
                         'giftcount':sms.giftcount,
                         'province':sms.province,
                         'city':sms.city,
                         'district':sms.district,
                         'pharmacyaddress':sms.pharmacyaddress,
                         'date':str(sms.date),
                         'receive':sms.receive,
                         'status':sms.status,
                         'id':sms.id

})
    return jsonify(result=sms_list)

@admin.route('/user/khsllq', methods=['POST'])
@login_required
def khsllq():
    if request.method == 'POST':
        try:
            id = request.form['id']
            print id
            qxhkdj = QXHKHDJ.query.get(id)
            if qxhkdj:
                qxhkdj.receive = 1
                db.session.add(qxhkdj)
                db.session.commit()
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('UPDATE KHSLLQ ERROR,%s'%e)
            return jsonify(result=False,error=e.message)

@admin.route('/user/khsljjlq', methods=['POST'])
@login_required
def khsljjlq():
    if request.method == 'POST':
        try:
            id = request.form['id']
            print id
            qxhkdj = QXHKHDJ.query.get(id)
            if qxhkdj:
                qxhkdj.receive = 2
                db.session.add(qxhkdj)
                db.session.commit()
                for codes in qxhkdj.qxhcodes:
                    codes.qxhkjdj_id = None
                    db.session.add(qxhkdj)
                    db.session.commit()

            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('UPDATE KHSLLQ ERROR,%s'%e)
            return jsonify(result=False,error=e.message)

@admin.route('/user/khsldjqx', methods=['POST'])
@login_required
def khsldjqx():
    if request.method == 'POST':
        try:
            id = request.form['id']
            print id
            qxhkdj = QXHKHDJ.query.get(id)
            if qxhkdj:
                qxhkdj.status = 0
                db.session.add(qxhkdj)
                db.session.commit()
                for codes in qxhkdj.qxhcodes:
                    codes.qxhkjdj_id = None
                    db.session.add(qxhkdj)
                    db.session.commit()

            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            current_app.logger.error('UPDATE KHSLLQ ERROR,%s'%e)
            return jsonify(result=False,error=e.message)


#@admin.route('/user/servicetype/<int:user_id>', methods=['POST'])
#@login_required
#def user_servicetype(user_id):
#    if request.method == 'POST':
#        try:
#            user = User.query.get(user_id)
#            is_isable = int(request.form['servicetype'])
#            isable_reason = request.form['isable_reason']
#            user.is_isable = is_isable
#            user.isable_reason = isable_reason
#            db.session.commit()
#            return jsonify(result=True)
#        except Exception,e:
#            db.session.rollback()
#            current_app.logger.error('USERSERVICE ISABLE ERROR,%s'%e)
#            return jsonify(result=False,error=e.message)


@admin.route('/user/servicetype/<int:user_id>',methods=['POST'])
@login_required
def user_servicetype(user_id):
    if request.method=='POST':
        user = User.query.get_or_404(user_id)
        #reason = request.form['reason']
        is_isable = int(request.form['servicetype'])
        if is_isable:
            ss = '停用'
        else:
            ss = '启用'
        isable_reason = request.form['isable_reason']
        if user.assign_operator_id<>current_user.id:
            return jsonify(result=False,error=u'该客户不归属于你，无法%s。'%ss)
        _conditions = []
        _conditions.append(User_Isable.user_id == user_id)
        _conditions.append(User_Isable.status == 0)
        giveupuserdata = User_Isable.query.filter(db.and_(*_conditions)).limit(1)
        giveupusers = []
        for g in giveupuserdata:
            giveupusers.append(g.id)
        if len(giveupusers) > 0:
            return jsonify(result=False,error=u'该客户正在%s审核中。'%ss)
        try:
            giveupuser = User_Isable();
            giveupuser.user_id = user_id
            giveupuser.operator_id = current_user.id
            giveupuser.reason = isable_reason
            giveupuser.is_isable = is_isable
            db.session.add(giveupuser)
            db.session.commit()
            current_app.logger.info('USERSERVICE ISABLE|%s|%s|%s|%s'%(user.user_id,is_isable,current_user.id,datetime.now()))
            return jsonify(result=True)
        except Exception,e:
            db.session.rollback()
            return jsonify(result=False,error=u'无法%s该客户，%s'%(ss,e))


@admin.route('/user/servicetypeok',methods=['POST'])
@admin_required
def servicetype_user_ok():
    try:
        sel_ids = json.loads(request.form['ids'])
        user_ids = map(lambda s:int(s),sel_ids)
        remarks = request.form['remarks']
        if len(user_ids)==0:return jsonify(result=False,error=u'请先选择要放弃归属的客户！')
        users = User.query.filter(User.user_id.in_(user_ids))
        # for u in users:
        #     if not op.assign_user_type&u.user_type:
        #         return jsonify(result=False,error=u'员工《%s》指派类型和客户《%s》当前类型不匹配！'%(op.nickname,u.name))

#        for u in users:
#            u.assign_operator_id = None
#            u.assign_retain_time = 0
#            u.is_abandon = True
#            u.assign_op(None,current_user.id,True)
#
#            current_app.logger.info('DROP_USER|%s|%s|%s|%s'%(current_user.id,current_user.id,u.user_id,u.assign_operator_id))

        servicetypes = User_Isable.query.filter(db.and_(User_Isable.user_id.in_(user_ids),User_Isable.status == 0)).all()
        for give in servicetypes:
            give.status = 1
            give.audit_operator_id = current_user.id
            give.audit_time = datetime.now()
            give.remarks = remarks

            give.user.is_isable = give.is_isable
            give.user.isable_reason = give.remarks
            current_app.logger.info('USERSERVICEOK ISABLE|%s|%s|%s|%s'%(give.user_id,give.is_isable,current_user.id,datetime.now()))
        #db.session.query(User_Giveup).filter(User_Giveup.user_id.in_(user_ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify(result=True)
    except Exception,e:
        printException()
        db.session.rollback()
        current_app.logger.error('DROP_USER ERROR.%s'%e)
        return jsonify(result=False,error=e.message)

@admin.route('/user/servicetypeno',methods=['POST'])
@admin_required
def servicetype_user_no():
    try:
        sel_ids = json.loads(request.form['ids'])
        user_ids = map(lambda s:int(s),sel_ids)
        remarks = request.form['remarks']
        if len(user_ids)==0:return jsonify(result=False,error=u'请先选择要放弃归属的客户！')
        users = User.query.filter(User.user_id.in_(user_ids))
        # for u in users:
        #     if not op.assign_user_type&u.user_type:
        #         return jsonify(result=False,error=u'员工《%s》指派类型和客户《%s》当前类型不匹配！'%(op.nickname,u.name))

#        for u in users:
#            current_app.logger.info('DROP_USERNO|%s|%s|%s|%s'%(current_user.id,current_user.id,u.user_id,u.assign_operator_id))

        servicetypes = User_Isable.query.filter(db.and_(User_Isable.user_id.in_(user_ids),User_Isable.status == 0)).all()
        for give in servicetypes:
            give.status = 2
            give.audit_operator_id = current_user.id
            give.audit_time = datetime.now()
            give.remarks = remarks

            current_app.logger.info('USERSERVICENO ISABLE|%s|%s|%s|%s'%(give.user_id,give.is_isable,current_user.id,datetime.now()))

        
        db.session.commit()
        return jsonify(result=True)
    except Exception,e:
        printException()
        db.session.rollback()
        current_app.logger.error('DROP_USER ERROR.%s'%e)
        return jsonify(result=False,error=e.message)



@admin.route('/user/servicetypes')
@admin_required
def servicetype_users():
    _conditions = user_conditions()
    #仅允许管理本部门员工数据
    #if not current_user.is_admin and current_user.team:
    #    operators = Operator.query.filter(db.and_(Operator.team.like(current_user.team+'%'),Operator.assign_user_type>0))
    #    op_ids = [op.id for op in operators]
    #    _conditions.append(User.assign_operator_id.in_(op_ids))
    #else:
    operators = Operator.query.filter(Operator.assign_user_type>0)

    page = int(request.args.get('page', 1))
    _conditions.append(User_Isable.status==0)
    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User.join_time)
    if len(_conditions) > 0:
        pagination = User_Isable.query.filter(db.and_(*_conditions)).join(User,User.user_id==User_Isable.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    else:
        pagination = User_Isable.query.filter(db.and_(User_Isable.status == 0)).join(User,User.user_id==User_Isable.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/servicetype_fq.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])


@admin.route('/user/servicetype_sq')
@admin_required
def servicetype_user_sq():
    _conditions = user_conditions()
    operators = Operator.query.filter(Operator.assign_user_type>0)

    page = int(request.args.get('page', 1))
    _conditions.append(User_Isable.operator_id == current_user.id)
    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User_Isable.created)
    if len(_conditions) > 0:
        pagination = User_Isable.query.filter(db.and_(*_conditions)).join(User,User.user_id==User_Isable.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    else:
        pagination = User_Isable.query.filter(db.and_(User_Giveup.status == 0)).join(User,User.user_id==User_Isable.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    return render_template('user/servicetype_sq.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])

@admin.route('/user/servicetype_audit')
@admin_required
def servicetype_user_audit():
    _conditions = user_conditions()
    operators = Operator.query.filter(Operator.assign_user_type>0)

    page = int(request.args.get('page', 1))
    _conditions.append(User_Isable.audit_operator_id == current_user.id)
    is_order,order_by = user_order_by()
    if not is_order:order_by = desc(User_Isable.created)
    #_conditions.append(User_Isable.status == 0)
    pagination = User_Isable.query.filter(db.and_(*_conditions)).join(User,User.user_id==User_Isable.user_id).order_by(order_by).paginate(page, per_page=user_per_page())
    
    return render_template('user/servicetype_sq.html',
                           pagination=pagination,
                           operators=operators,
                           show_queries=['admin','user_origin','op','user_type','username','phone','show_abandon'])

@admin.route('/user/showfwtjfg/<int:user_id>')
@login_required
def user_show_fwtjfg(user_id):
    _objs = User_tjfg.query.filter(User_tjfg.user_id==user_id)
    sms_list = []
    for sms in _objs:
        sms_list.append({'message':str(sms.created),
                         'bigcount':sms.bigcount,
                         'mediumcount':sms.mediumcount,
                         'smallcount':sms.smallcount

})

    return jsonify(result=sms_list)
