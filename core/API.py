#coding=utf-8
from collections import defaultdict,OrderedDict
from datetime import datetime
from extensions import db
from flask import render_template,Blueprint,request,jsonify

from settings.constants import *
from models import Order
from utils.decorator import cached

api = Blueprint('api',__name__,url_prefix='/api')

@api.route('/order/status/batch',methods=['POST'])
def order_status_batch():
    order_ids = request.form['ids'].split(',')
    orders = Order.query.filter(Order.order_id.in_(order_ids))
    _list = []
    for order in orders:
        _list.append({'order_id':order.order_id,
                     'status':order.status,
                     'status_name':order.status_name,
                     'fee':order.actual_fee,
                     'payment_type':order.payment_type,
                     'payment_type_name':order.payment_type_name})
    return jsonify(list=_list)

@api.route('/order/status/<int:order_id>')
def order_status_by_id(order_id):
    order = Order.query.get(order_id)
    if not order:
        res = jsonify(error=404,description=u'订单不存在')
        res.status_code = 404
        return res

    return jsonify(order_id=order.order_id,
                   status=order.status,
                   status_name=order.status_name,
                   fee=order.actual_fee,
                   payment_type = order.payment_type,
                   payment_type_name = order.payment_type_name)