# -*- coding: utf-8 -*-
from collections import defaultdict,OrderedDict
from datetime import datetime,timedelta

from extensions import db

from flask.ext.login import current_user

from flask import render_template,Blueprint,request
from utils.decorator import admin_required
from .models import Order_Operator,Outbound,Knowledge,Knowledge_Category,User_Statistics,Order_LHYD_Postal,Security_Code,Security_Code_Log,User_Giveup,User_Assign_Log,SMS,Operator, Role, Item, Sku,Sku_Stock,Stock_Out, Stock_In, Sku_Set,Loss, Stock, IO_Log, Order, Order_Sets, Order_Log, User, User_Dialog, User_Phone, Address, Order_Item, News#Permission,Role,
from sqlalchemy import desc,asc,func
from sqlalchemy.orm import defer

from settings.constants import *
import sys
joinexport = Blueprint('joinexport',__name__,url_prefix='/joinexport')
#导出心力健的数据
@joinexport.route('/dcd20140418')
@admin_required
def john_dcd20140418():
    _conditions = [Order.order_type==14]
    _conditions.append('`order`.created_by in (127,126,124,123,121,119,130,135,122)')
    _conditions.append('`user`.join_time<\'2014-04-01\'')

    pagination = User.query.outerjoin(Order,User.assign_operator_id==Order.created_by).filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id left join `order` on `order`.order_id=stock_in.order_id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    #pagination = db.session.query('select stock_in.order_id,sku.name,`order`.express_id from stock_in left join sku on   stock_in.sku_id=sku.id   where stock_in.created>\'2013-09-01\' and stock_in.created<\'2013-10-01\'')
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

#导出1311月新客户公共库
@joinexport.route('/dcd201404182')
@admin_required
def john_dcd201404182():
    _conditions = [User.user_type==1]
    _conditions.append(User.assign_operator_id == None)
    _conditions.append('(`user`.join_time>\'2013-11-01\' and `user`.join_time<\'2013-12-01\')')

    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#导出1312月新客户公共库
@joinexport.route('/dcd20140423')
@admin_required
def john_dcd20140423():
    _conditions = [User.user_type==1]
    _conditions.append(User.assign_operator_id == None)
    _conditions.append('(`user`.join_time>\'2013-10-01\' and `user`.join_time<\'2013-11-01\')')

    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#导出1312月新客户公共库
@joinexport.route('/dcd201404231')
@admin_required
def john_dcd201404231():
    _conditions = [User.user_type==1]
    _conditions.append(User.assign_operator_id == None)
    _conditions.append('(`user`.join_time>\'2013-07-01\' and `user`.join_time<\'2013-09-01\')')

    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
@joinexport.route('/dcd201404232')
@admin_required
def john_dcd201404232():
    _conditions = [User.assign_operator_id == 89]
    #_conditions.append('(`user`.user_id=48312 or `user`.remark like \'气血和%\' or `user`.origin=12 or `user`.product_intention=0)')

    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcname.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

#导出会员客户公共库
@joinexport.route('/dcd20140513')
@admin_required
def john_dcd20140513():
    _conditions = [User.user_type==2]
    pagination = User.query.filter(*_conditions).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

#导出维护宅急送
@joinexport.route('/dcd20140519')
@admin_required
def john_dcd20140519():
    _conditions = []
    #_conditions.append("user.assign_operator_id in (select id from operator where team='C1' OR team='C2')" )
    _conditions.append("order.team='C1' OR order.team='C2'" )
    _conditions.append(Order.created >= '2014-01-01')
    _conditions.append(Order.created <= '2014-05-01')
    _conditions.append(Order.express_number == 2)
    pagination = User.query.join(Order, Order.user_id == User.user_id).filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#导出外呼 外呼组 TQ组 
@joinexport.route('/dcd20140620')
@admin_required
def john_dcd20140620():
    _conditions = []
    _conditions.append("user.assign_operator_id in (select id from operator where team='B1' OR team='B2')" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(Order.created >= '2014-01-01')
    #_conditions.append(Order.created <= '2014-05-01')
    #_conditions.append(Order.express_number == 2)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
#导出废弃(会员客户)
@joinexport.route('/dcd20140626')
@admin_required
def john_dcd20140626():
    _conditions = []
    _conditions.append("user.assign_operator_id =89" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(Order.created >= '2014-01-01')
    #_conditions.append(Order.created <= '2014-05-01')
    #_conditions.append(Order.express_number == 2)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

#接线 55小时
@joinexport.route('/dcd20140627')
@admin_required
def john_dcd20140627():
    _conditions = []
    _conditions.append("assign_operator_id in (select id from operator where team='A2')" )
    #_conditions.append("assign_time>0")
    _conditions.append("order_num=0")
    _conditions.append("ADDDATE(assign_time,interval 55 hour)<now()")
    pagination = User.query.filter(db.and_(*_conditions))#.order_by(desc(User.assign_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
@joinexport.route('/dcd20140702')
@admin_required
def john_dcd20140702():
    _conditions = []
    _conditions.append("user.assign_operator_id in (37,39,57,123,59,60,61,85,86,91,124,92,98,102,112,125,135,137)" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(Order.created >= '2014-01-01')
    #_conditions.append(Order.created <= '2014-05-01')
    #_conditions.append(Order.express_number == 2)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

#导出新客户公共库
@joinexport.route('/dcd20140903')
@admin_required
def john_dcd20140903():
    _conditions = [User.user_type==1]
    _conditions.append(User.origin<>18)
    _conditions.append(User.origin<>11)
    _conditions.append(User.join_time >= '2014-05-01')
    _conditions.append(User.join_time <= '2014-09-01')    
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

#导出高霞
@joinexport.route('/dcd201409031')
@admin_required
def john_dcd201409031():
    _conditions = [User.user_type==2]
    _conditions.append(User.origin>12)
    _conditions.append(User.origin<18)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcgx.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20140904')
@admin_required
def john_dcd20140904():
    _conditions = [User.user_type==2]
    _conditions.append(User.origin>12)
    _conditions.append(User.origin<15)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcgx.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd201409041')
@admin_required
def john_dcd201409041():
    _conditions = [User.user_type==2]
    _conditions.append(User.origin<>18)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcg20140915')
@admin_required
def john_dcg20140915():
    _conditions = [User.user_type==2]
    _conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

#导出心力健的数据
@joinexport.route('/dcjohn')
@admin_required
def john_dcjohn():
    sql = """SELECT DATE_FORMAT(`order`.created,'%Y-%m'),`address`.province,sum(distinct `order`.item_fee) from `order` join `address` on address.id=`order`.shipping_address_id 
         WHERE `order`.order_type=15 AND `order`.status NOT IN (1,103) and `order`.status<200 group by `address`.province,DATE_FORMAT(`order`.created,'%Y-%m') order by `address`.province,DATE_FORMAT(`order`.created,'%Y-%m')
"""

    pagination = db.session.query(sql)
    return render_template('john/dcjohn.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

                     
@joinexport.route('/dcd20140916')
@admin_required
def john_dcd20140916():
    _conditions = []
    _conditions.append("user.assign_operator_id in (4,90,113,38,147)" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    _conditions.append(User.join_time >= '2014-05-01')
    #_conditions.append(Order.express_number == 2)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20140916.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
 
@joinexport.route('/dcd20141014')
@admin_required
def john_dcd20141014():
    _conditions = []
    _conditions.append("(user.assign_operator_id in (4,90,113,38,147) and user.product_intention in (0,2,3,4))")# (0,2,3,4))" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    _conditions.append(User.join_time >= '2014-01-01')
    _conditions.append(User.join_time < '2014-05-01')
    #_conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dc20141016')
@admin_required
def john_dc20141016():
    _conditions = []
    _conditions.append("user.user_type=2 and user.assign_operator_id is not null  and user.product_intention = 0" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20141125')
@admin_required
def john_dc20141125():

    _conditions = []
    _conditions.append("(user.assign_operator_id in (4,90,113,38,147) or (user.user_type=1 and user.product_intention <> 11))")# (0,2,3,4))" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    _conditions.append(User.join_time >= '2014-08-01')
    _conditions.append(User.join_time < '2014-10-01')
    #_conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150106')
@admin_required
def john_dc20150106():

    _conditions = []
    _conditions.append(User.user_type == 2)
    _conditions.append(User.join_time >= '2014-06-01')
    _conditions.append(User.join_time < '2015-01-01')
    #_conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20150106.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150115')
@admin_required
def john_dc20150115():

    _conditions = []
    _conditions.append(User.user_type == 2)
    #_conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20150115.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150116')
@admin_required
def john_dcd20150116():

    _conditions = []
    _conditions.append(User.user_type == 1)
    #_conditions.append(User.user_type == 2)
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    _conditions.append(User.join_time >= '2014-09-01')
    _conditions.append(User.join_time < '2014-12-01')
    #_conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])
@joinexport.route('/dcd20150120')
@admin_required
def john_dc20150120():

    _conditions = []
    _conditions.append(User.product_intention == 7)
    #_conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20150120.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150212')
@admin_required
def john_dc20150212():

    _conditions = []
    _conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(User.user_type == 2)
    #_conditions.append(User.product_intention == 1)
    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150326')
@admin_required
def john_dc20150326():

    _conditions = []
    _conditions.append("user.user_type=1 and user.assign_operator_id is null  and user.product_intention = 0" )
    #_conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(User.user_type == 1)
    #_conditions.append(User.product_intention == 0)
    _conditions.append(User.join_time >= '2015-01-01')
    _conditions.append(User.join_time < '2015-03-01')

    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150408')
@admin_required
def john_dc20150408():

    _conditions = []
    _conditions.append("user.user_type=1 and user.assign_operator_id is null  and user.product_intention = 0" )
    #_conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(User.user_type == 1)
    #_conditions.append(User.product_intention == 0)
    _conditions.append(User.join_time >= '2014-01-01')
    _conditions.append(User.join_time < '2014-09-01')

    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150417')
@admin_required
def john_dc20150417():

    _conditions = []
    _conditions.append("user.user_type=2 and user.assign_operator_id is not null  and user.weixin is not null" )
    #_conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(User.user_type == 1)
    #_conditions.append(User.product_intention == 0)
    #_conditions.append(User.join_time >= '2014-01-01')
    #_conditions.append(User.join_time < '2014-09-01')

    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20150417.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150423')
@admin_required
def john_dc20150423():

    _conditions = []
    _conditions.append("((user.user_type=1 and user.assign_operator_id is null) or user.assign_operator_id in (select id from operator where team like 'A%' OR  team like 'B%')) and user.product_intention = 1" )
    #_conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    #_conditions.append("order.team='B1' OR order.team='B2'" )
    #_conditions.append(User.user_type == 1)
    #_conditions.append(User.product_intention == 0)
    #_conditions.append(User.join_time >= '2014-01-01')
    #_conditions.append(User.join_time < '2014-09-01')

    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150429')
@admin_required
def john_dc20150429():

    _conditions = []
    #_conditions.append("((user.user_type=2 and user.assign_operator_id is null) or user.assign_operator_id in (select id from operator where team like 'A%' OR  team like 'B%')) and user.product_intention = 1" )
    #_conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    _conditions.append("user.user_type=2" )
    #_conditions.append(User.user_type == 1)
    #_conditions.append(User.product_intention == 0)
    #_conditions.append(User.join_time >= '2014-01-01')
    #_conditions.append(User.join_time < '2014-09-01')

    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20150429.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd201500611')
@admin_required
def john_dc20150611():

    _conditions = []
    _conditions.append("user.user_type=1 and user.assign_operator_id is null" )
    #_conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    #_conditions.append("user.user_type=1" )
    _conditions.append(User.product_intention == 0)
    _conditions.append(User.join_time >= '2015-01-01')
    _conditions.append(User.join_time < '2015-06-01')

    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20131111.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150612')
@admin_required
def john_dc20150612():

    _conditions = []
    #_conditions.append("user.user_type=1 and user.assign_operator_id is null" )
    #_conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    #_conditions.append("user.user_type=1" )
    _conditions.append(User.origin == 18)
    _conditions.append(User.is_valid == 2)

    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20150612.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd201506122')
@admin_required
def john_dc201506122():

    _conditions = []
    _conditions.append("user.origin in (17,18) and user_id in (select user_id from qxhdm_orderyf)" )
    #_conditions.append("(user.assign_operator_id in (8,40,41,42,43,45,47,48,84,87,154,194,201,210,231,232,227,228,229,219,222,223,224,225) or user.user_type=2)")# (0,2,3,4))" )
    #_conditions.append("user.user_type=1" )
    _conditions.append(User.join_time < '2015-03-01')

    pagination = User.query.filter(db.and_(*_conditions)).order_by(desc(User.expect_time))
    print pagination
    return render_template('john/dcd20150612.html',
                           pagination=pagination,
                           show_queries=['user_origin','op','user_type','username','phone','show_abandon'])

@joinexport.route('/dcd20150625')
@admin_required
def john_dc20150625():
    reload( sys )
    sys.setdefaultencoding('utf-8')
    _sql = '''SELECT `user`.user_id,`user`.phone,`order`.item_fee-`order`.discount_fee,`order_item`.name,`order_item`.price,`order_item`.quantity,`order_item`.fee FROM `order_item`
JOIN `order` ON `order_item`.order_id=`order`.order_id AND `order`.delivery_time IS NOT NULL
JOIN `user` on `user`.user_id=`order`.user_id
JOIN `operator` ON `operator`.id=`order`.created_by
WHERE `order`.status not in (1,103) and `user`.product_intention=8 and `user`.join_time>'2014-12-01' and `user`.join_time<'2015-06-01'
'''
    rows = db.session.execute(_sql)
    data = OrderedDict()
    for user_id,phone,fee,item_name,price,quantity,item_fee in rows:
        if not data.has_key(user_id):
            data[user_id] = {
                              'phone':phone,
                              'items':[]
                              }
        data[user_id]['items'].append({'name':item_name,'num':quantity,'fee':item_fee,'price':price})
    _data = data.values()
    _data = sorted(_data,key=lambda d:d['user_id'])
    print _data
    return render_template('john/dcd20150625.html',data=_data)

@joinexport.route('/dcd20151026')
@admin_required
def john_dc20151026():
    _conditions = ['''user_id in (select user_id from user where assign_operator_id in (SELECT id from operator where team like 'C%'))''']
    _conditions.append("created<'2015-06-01' and created=(SELECT max(created) from `order` as b where `order`.user_id=b.user_id)")
    _data = Order.query.filter(db.and_(*_conditions))
    
    print _data
    return render_template('john/dcd20151026.html',data=_data)


