#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os.path
from datetime import datetime
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask.ext.script import Manager
from app import create_app
from settings.constants import  *

from utils.memcached import cache

_app = create_app()
manager = Manager(_app)

from extensions import db

from core import models
from analytics.models import *

def color(text,color,bold=True):
    if color=='green':
        return '\x1b[32%sm%s\x1b[0m'%(';%s'%int(bold) if bold else '',text)
    elif color=='blue':
        return '\x1b[34%sm%s\x1b[0m'%(';%s'%int(bold) if bold else '',text)
    elif color=='red':
        return '\x1b[31%sm%s\x1b[0m'%(';%s'%int(bold) if bold else '',text)
    elif color=='yellow':
        return '\x1b[33%sm%s\x1b[0m'%(';%s'%int(bold) if bold else '',text)
    elif color=='gray':
        return '\x1b[35%sm%s\x1b[0m'%(';%s'%int(bold) if bold else '',text)
    return text

def confirm(txt):
    if raw_input('%s %s:'%(color(txt,'yellow'),color('(y/n)','red'))).lower()<>'y':
        print 'aborted.'
        sys.exit(0)


@manager.command
def cache_test():
    k = 'TEST'
    v = cache.get(k)
    if v:
        print 'exists = ',v
    else:
        cache.set(k,'1000')
        print 'no exists'


@manager.command
def init_db():
    '''init database'''
    db.create_all()
    print 'Init database success.'

@manager.command
def drop_db():
    '''drop database'''
    db.drop_all()
    print 'Drop database success.'


# @manager.command
# def import_xl_user():
#     '''导入兴龙客户资料'''
#     xl_users = []
#     _conn = db.engine.connect()
#     try:
#         datas = _conn.execute('''
#         SELECT name,phone,phone_1,address,dialog_content,op_id,create_date FROM `ai7mtest`.`xl_user` as `tmp_user`
#         ''')
#         for d in datas:xl_users.append(d)
#     except Exception,e:
#         print e
#         sys.exit(0)
#
#     repeat_user_nums = 0
#     import_user_nums = 0
#     error_user_nums = 0
#     for name,phone,phone_1,street,dialog_content,op_id,create_date in xl_users:
#         dialog_content = '\r\n'.join([c for c in dialog_content.split() if c])
#         try:
#             if models.User_Phone.user_id_by_phone(phone) or models.User_Phone.user_id_by_phone(phone_1):
#                 print name,phone
#                 repeat_user_nums += 1
#                 _conn.execute('UPDATE `ai7mtest`.`xl_user` SET flag=9 WHERE `phone`="%s" AND `flag`=0'%phone)
#                 _conn.execute('COMMIT')
#                 continue
#
#             user = models.User()
#             user.name = name
#             user.phone = phone
#             user.phone2 = phone_1
#
#             user.user_type = 2
#             user.assign_operator_id = op_id
#             user.assign_time = datetime.now()
#             user.is_assigned = True
#             user.operator_id = op_id
#
#             if dialog_content:
#                 user.dialog_times = 1
#                 user.last_dialog_time = datetime.now()
#
#             user.origin = 2
#             user.batch_id = 'XL20130507'
#             user.join_time = create_date
#
#             db.session.add(user)
#             db.session.flush()
#
#             if phone:
#                 db.session.add(models.User_Phone.add_phone(user.user_id,phone))
#
#             if phone_1:
#                 db.session.add(models.User_Phone.add_phone(user.user_id,phone_1))
#
#
#             #添加客户地址
#             if street:
#                 address = models.Address()
#                 address.user_id = user.user_id
#                 address.street1 = street
#                 address.ship_to = name
#                 address.phone = phone
#                 if phone_1:address.tel = phone_1
#                 db.session.add(address)
#                 db.session.flush()
#
#             if dialog_content:
#                 dialog = models.User_Dialog()
#                 dialog.user_id = user.user_id
#                 dialog.operator_id = op_id
#                 dialog.type = 0
#                 dialog.content = dialog_content
#                 dialog.solution = ''
#                 dialog.created = create_date
#                 db.session.add(dialog)
#             db.session.commit()
#             import_user_nums += 1
#             _conn.execute('UPDATE `ai7mtest`.`xl_user` SET flag=1 WHERE `phone`="%s" AND `flag`=0'%phone)
#             _conn.execute('COMMIT')
#         except Exception,e:
#             print e
#             db.session.rollback()
#             break
#
#     print '-'*20
#     print 'repeat user:',repeat_user_nums
#     print 'import user:',import_user_nums




# @manager.command
# def import_user():
#     '''导入客户资料'''
#     pre_import_users = []
#     _conn = db.engine.connect()
#     try:
#         datas = _conn.execute('''
#         SELECT name,phone,gender,street,op_id,user_origin,user_type,join_time FROM `ai7mtest`.`bx_user`
#         ''')
#         for d in datas:pre_import_users.append(d)
#     except Exception,e:
#         print e
#         sys.exit(0)
#
#     confirm(u'确认导入客户（%s）？'%len(pre_import_users))
#
#     repeat_user_nums = 0
#     import_user_nums = 0
#     error_user_nums = 0
#     assign_user_nums = 0
#     for name,phone,gender,street,op_id,user_origin,user_type,join_time in pre_import_users:
#         try:
#             _user_id_1 = models.User_Phone.user_id_by_phone(phone)
#             if _user_id_1:
#                 print name,phone
#                 repeat_user_nums += 1
#
#                 # #调配公共库客户归属
#                 # __user_id = _user_id_1 or _user_id_2
#                 # try:
#                 #     user = models.User.query.get(__user_id)
#                 #     if user.user_type == 2 and not user.assign_operator_id:
#                 #         user.assign_operator_id = op_id
#                 #         user.assign_time = datetime.now()
#                 #         user.assign_retain_time = 0
#                 #         db.session.commit()
#                 #         assign_user_nums += 1
#                 # except:
#                 #     pass
#                 continue
#
#             user = models.User()
#             user.name = name
#             user.phone = phone
#             user.gender = gender
#             #user.phone2 = phone2
#
#             user.origin = user_origin
#             user.user_type = user_type
#             user.assign_time = datetime.now()
#             if op_id:
#                 user.assign_operator_id = op_id
#                 user.is_assigned = True
#                 assign_user_nums += 1
#                 user.operator_id = op_id
#                 user.assign_time = datetime.now()
#                 user.assign_retain_time = USER_ASSIGN_HOURS.get(user_origin, 72) if user_type == 1 else 0
#             else:
#                 user.operator_id = 6
#
#
#             user.batch_id = 'BX20130509'
#             #user.join_time = datetime.now()
#             user.join_time = join_time
#
#             db.session.add(user)
#             db.session.flush()
#
#             db.session.add(models.User_Phone.add_phone(user.user_id,phone))
#
#             #添加客户地址
#             if street:
#                 address = models.Address()
#                 address.user_id = user.user_id
#                 address.street1 = street
#                 address.ship_to = name
#                 address.phone = phone
#                 db.session.add(address)
#                 db.session.flush()
#
#             db.session.commit()
#             import_user_nums += 1
#         except Exception,e:
#             print e
#             db.session.rollback()
#             break
#
#     print '-'*20
#     print u'导入客户完成，客户总数：%s；成功导入客户：%s；重复客户数：%s；公共库客户数：%s'%(len(pre_import_users),import_user_nums,repeat_user_nums,import_user_nums-assign_user_nums)
#

@manager.command
def import_user_0731():
    '''导入客户资料'''
    pre_import_users = []
    _conn = db.engine.connect()
    try:
        datas = _conn.execute('''
        SELECT name,phone,address,order_info FROM `ai7mtest`.`user_0731`
        ''')
        for d in datas:pre_import_users.append(d)
    except Exception,e:
        print e
        sys.exit(0)

    confirm(u'确认导入客户（共计：%s）？'%len(pre_import_users))

    repeat_user_nums = 0
    import_user_nums = 0
    error_user_nums = 0
    assign_user_nums = 0
    for name,phone,addr,info in pre_import_users:
        try:
            _user_id_1 = models.User_Phone.user_id_by_phone(phone)
            #_user_id_2 = models.User_Phone.user_id_by_phone(phone2)
            #_user_id_3 = models.User_Phone.user_id_by_phone(tel)
            if _user_id_1:# or _user_id_2 or _user_id_3:
                print 'REPEAT   %s'%phone
                repeat_user_nums += 1

                #调配公共库客户归属
                # __user_id = _user_id_1 or _user_id_2
                # try:
                #     user = models.User.query.get(__user_id)
                #     if user.user_type == 2 and not user.assign_operator_id:
                #         user.assign_operator_id = op_id
                #         user.assign_time = datetime.now()
                #         user.assign_retain_time = 0
                #         db.session.commit()
                #         assign_user_nums += 1
                # except:
                #     pass
                continue

            user = models.User()
            user.name = name
            user.phone = phone
            #user.gender = gender
            #user.phone2 = phone2
            #user.tel = tel

            user.origin = 99#user_origin
            user.user_type = 1
            user.assign_operator_id = 4
            user.is_assigned = True
            user.operator_id = 4
            user.assign_time = datetime.now()
            user.assign_retain_time = 0
            # if op_id:
            #     user.assign_operator_id = op_id
            #     user.is_assigned = True
            #     assign_user_nums += 1
            #     user.operator_id = op_id
            #     user.assign_time = datetime.now()
            #     user.assign_retain_time = USER_ASSIGN_HOURS.get(user_origin, 72) if user_type == 1 else 0
            # else:
            #     user.operator_id = 6

            user.remark = u'外购'


            user.batch_id = '20130731'
            #user.join_time = datetime.now()
            user.join_time = datetime.now()

            db.session.add(user)
            db.session.flush()
            db.session.add(models.User_Phone.add_phone(user.user_id,phone))

            # if phone2:
            #     db.session.add(models.User_Phone.add_phone(user.user_id,phone2))
            #
            # if tel:
            #     db.session.add(models.User_Phone.add_phone(user.user_id,tel))

            #添加客户地址
            if addr:
                address = models.Address()
                address.user_id = user.user_id
                address.street1 = addr
                address.ship_to = name
                address.phone = phone
                db.session.add(address)
                db.session.flush()

            #添加订购信息沟通记录
            if info:
                dialog = models.User_Dialog()
                dialog.user_id = user.user_id
                dialog.operator_id = 4
                dialog.type = 0
                dialog.content = info
                dialog.solution = ''
                dialog.created = datetime.now()
                db.session.add(dialog)

            #db.session.execute('INSERT INTO `ai7mtest`.`phone_20130718`(phone) VALUES("%s")'%phone)

            # for p in (phone,phone2,tel):
            #     if p and p.startswith('1') and not p.startswith('10') and len(p)==11:
            #         db.session.execute('INSERT INTO `ai7mtest`.`phone_20130715`(phone) VALUES("%s")'%p)
            db.session.commit()
            import_user_nums += 1
        except Exception,e:
            print e
            db.session.rollback()
            break

    print '-'*20
    print u'导入客户完成，客户总数：%s；成功导入客户：%s；重复客户数：%s；调配客户数：%s'%(len(pre_import_users),import_user_nums,repeat_user_nums,assign_user_nums)


@manager.command
def import_user():
    '''导入客户资料'''
    pre_import_users = []
    _conn = db.engine.connect()
    try:
        datas = _conn.execute('''
        SELECT phone,phone2,tel,op_id,user_type FROM `ai7mtest`.`user_0718`
        ''')
        for d in datas:pre_import_users.append(d)
    except Exception,e:
        print e
        sys.exit(0)

    confirm(u'确认导入客户（共计：%s）？'%len(pre_import_users))

    repeat_user_nums = 0
    import_user_nums = 0
    error_user_nums = 0
    assign_user_nums = 0
    for phone,phone2,tel,op_id,user_type in pre_import_users:
        try:
            _user_id_1 = models.User_Phone.user_id_by_phone(phone)
            #_user_id_2 = models.User_Phone.user_id_by_phone(phone2)
            #_user_id_3 = models.User_Phone.user_id_by_phone(tel)
            if _user_id_1:# or _user_id_2 or _user_id_3:
                print 'REPEAT   %s  %s  %s'%(phone,phone2,tel)
                repeat_user_nums += 1

                #调配公共库客户归属
                # __user_id = _user_id_1 or _user_id_2
                # try:
                #     user = models.User.query.get(__user_id)
                #     if user.user_type == 2 and not user.assign_operator_id:
                #         user.assign_operator_id = op_id
                #         user.assign_time = datetime.now()
                #         user.assign_retain_time = 0
                #         db.session.commit()
                #         assign_user_nums += 1
                # except:
                #     pass
                continue

            user = models.User()
            user.name = u'0718导入'
            user.phone = phone
            #user.gender = gender
            #user.phone2 = phone2
            #user.tel = tel

            user.origin = 99#user_origin
            user.user_type = user_type
            user.assign_operator_id = op_id
            user.is_assigned = True
            user.operator_id = op_id
            user.assign_time = datetime.now()
            user.assign_retain_time = 0
            # if op_id:
            #     user.assign_operator_id = op_id
            #     user.is_assigned = True
            #     assign_user_nums += 1
            #     user.operator_id = op_id
            #     user.assign_time = datetime.now()
            #     user.assign_retain_time = USER_ASSIGN_HOURS.get(user_origin, 72) if user_type == 1 else 0
            # else:
            #     user.operator_id = 6


            user.batch_id = '20130718'
            #user.join_time = datetime.now()
            user.join_time = datetime.now()

            db.session.add(user)
            db.session.flush()

            db.session.add(models.User_Phone.add_phone(user.user_id,phone))

            # if phone2:
            #     db.session.add(models.User_Phone.add_phone(user.user_id,phone2))
            #
            # if tel:
            #     db.session.add(models.User_Phone.add_phone(user.user_id,tel))

            #添加客户地址
            # if street1:
            #     address = models.Address()
            #     address.user_id = user.user_id
            #     address.street1 = street1
            #     address.ship_to = name
            #     address.phone = phone
            #     db.session.add(address)
            #     db.session.flush()

            db.session.execute('INSERT INTO `ai7mtest`.`phone_20130718`(phone) VALUES("%s")'%phone)

            # for p in (phone,phone2,tel):
            #     if p and p.startswith('1') and not p.startswith('10') and len(p)==11:
            #         db.session.execute('INSERT INTO `ai7mtest`.`phone_20130715`(phone) VALUES("%s")'%p)
            db.session.commit()
            import_user_nums += 1
        except Exception,e:
            print e
            db.session.rollback()
            break

    print '-'*20
    print u'导入客户完成，客户总数：%s；成功导入客户：%s；重复客户数：%s；调配客户数：%s'%(len(pre_import_users),import_user_nums,repeat_user_nums,assign_user_nums)


@manager.command
def adjust_stock():
    __DATAS = [(10081,10068,10)]

    for from_sku_id,to_sku_id,quantity in __DATAS:
        from_sku = models.Sku.query.get(from_sku_id)
        to_sku = models.Sku.query.get(to_sku_id)

        if from_sku.actual_quantity<quantity:
            print color('%s库存不足，无法调库! - 1'%from_sku.name,'red')
            continue

        try:
            from_stock = models.Stock.stock_by_sku_id(from_sku.id,quantity)
            if not from_stock:
                print color('%s库存不足，无法调库! - 2'%from_sku.name,'red')
                continue

            from_stock.in_quantity = models.Stock.in_quantity - quantity
            from_sku.quantity = models.Sku.quantity - quantity

            stock = models.Stock()

            stock.sku_id = to_sku.id
            stock.store_id = from_stock.store_id
            stock.shelf_number = from_stock.shelf_number
            stock.code = from_stock.code
            stock.made_in = from_stock.made_in

            stock.mfg_date = from_stock.mfg_date
            stock.exp_date = from_stock.exp_date
            stock.in_quantity = quantity
            stock.purchase_price = from_stock.purchase_price
            stock.status = 9
            stock.operator_id = 1
            stock.remark = u'内部调库（%s）'%datetime.now().strftime('%Y.%m.%d')
            db.session.add(stock)

            to_sku.quantity = models.Sku.quantity + quantity
            db.session.commit()
            print color(from_sku.name,'green'),u' -> ',color(to_sku.name,'green'),u'数量：%s'%quantity
        except Exception,e:
            db.session.rollback()
            print color(u'%s调库失败,%s'%(from_sku.name,e),'red')
            continue

@manager.command
def test_sms():
    for phone in ('18628005095','15520737170'):
        models.SMS.add_sms(phone,u'断断续续洒洒说到底？收到勿回复！【董正选】',status=1,commit=True)

    # sms = models.SMS.add_sms('13438802101',u'一缺三？【董正选】',commit=True)#13982162376
    # sms = models.SMS.add_sms('13438802101',u'一缺三？【董正选】',commit=True)#13982162376sms = models.SMS.add_sms('13438802101',u'一缺三？【董正选】',commit=True)#13982162376

#print sms.send_url
    #print sms.send_sms()
    # res =  models.SMS.response('<?xml version="1.0" encoding="UTF-8"?><response><error>0</error><message></message></response>')
    # print res.error,res.message


@manager.command
def sendSMS():
    '''批量发送短信处理'''
    print 'start to send sms',
    SMS = models.SMS
    _all_sms = SMS.query.filter(db.or_(SMS.status==1,
                                       db.and_(SMS.status==9,SMS.fail_times<=3)))
    for sms in _all_sms:
        print '%d|%d'%(sms.seqid,int(sms.send_sms()))
    print 'complete.'


@manager.command
def init_data():
    '''init data'''
    _conn = db.engine.raw_connection()
    try:
        cursor = _conn.cursor()
        cursor.execute('set FOREIGN_KEY_CHECKS = 0')
        cursor.execute('COMMIT')
        #cursor.execute('TRUNCATE `role`')
        cursor.execute('TRUNCATE `operator`')
        cursor.execute("INSERT INTO `role` VALUES (101,'员工','A,orders,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,search_user_form,search_user,user,edit_user,add_user,update_address'),(102,'销售内勤','A,orders,order_search,order_approval,manage_order,order_detail,print_order_invoices,C,skus,sku_set_manage,B,search_user_form,search_user,manage_users,user,view_user_phone,sms_list,sms_approval,sms_mass,E,sale_report,sale_report_by_item,financial_report,financial_report_by_dzbb,financial_report_by_paidan,financial_report_by_paidan_tuihuo,financial_report_by_qianshou,financial_report_by_qianshou_tuihuo,logistics_report,logistics_report_by_day_delivery,logistics_report_by_loss,D'),(103,'财务','A,orders,order_search,order_approval,manage_order,order_detail,C,skus,E,financial_report,financial_report_by_sale,financial_report_by_return,financial_report_by_dzbb,financial_report_by_paidan,financial_report_by_paidan_tuihuo,financial_report_by_qianshou,financial_report_by_qianshou_tuihuo,logistics_report,logistics_report_by_day_delivery,logistics_report_by_io,logistics_report_by_loss,D,purchase_price,stock_in_list,stock_in_approval,stock_out_list,stock_out_approval'),(104,'物流','A,orders,order_search,order_approval,manage_order,edit_order,order_detail,print_order_invoices,order_fast_delivery,E,logistics_report,logistics_report_by_day_delivery,logistics_report_by_wlfhhz,logistics_report_by_io,logistics_report_by_loss,D,stock_in_list,add_stock_in,edit_stock_in,stock_out_list,add_stock_out,edit_stock_out,stock_delete'),(105,'物流内勤','A,orders,order_search,order_approval,manage_order,order_detail,E,financial_report,financial_report_by_dzbb'),(106,'销售主管','A,orders,order_search,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,public_new_users,search_user_form,search_user,manage_users,change_user_op,user,edit_user,add_user,update_address,E,sale_report,sale_report_by_ygxs,sale_report_by_staff,sale_report_by_team,sale_report_by_item,sale_report_by_ygdhtj,sale_report_by_ddxsmxtj,sale_report_by_arrival_detail,sale_report_by_arrival_total,sale_report_by_return_detail,sale_report_by_return_total,D'),(107,'产品管理','C,items,del_item,skus,edit_sku,add_sku,sku_set_manage,add_sku_set,update_sku_set_status,D,stock_in_list,add_stock_in,stock_out_list,add_stock_out'),(999,'系统管理员',NULL),(1000,'第三方商城','A,orders,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,search_user_form,search_user,user,edit_user,add_user,update_address'),(1001,'分销商','A,orders,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,search_user_form,search_user,user,edit_user,add_user,update_address'),(1002,'客情','A,orders,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,search_user_form,search_user,user,edit_user,add_user,update_address'),(1003,'维护主管','A,orders,order_search,add_order,order_approval,manage_order,edit_order,order_detail,except_orders,B,my_users,public_old_users,search_user_form,search_user,manage_users,change_user_op,user,edit_user,add_user,update_address,E,sale_report,sale_report_by_ygxs,sale_report_by_staff,sale_report_by_team,sale_report_by_item,sale_report_by_ygdhtj,sale_report_by_ddxsmxtj,sale_report_by_arrival_detail,sale_report_by_arrival_total,sale_report_by_return_detail,sale_report_by_return_total,D'),(1004,'总经办','A,orders,order_search,order_detail,user,E,sale_report,sale_report_by_ygxs,sale_report_by_staff,sale_report_by_team,sale_report_by_item,sale_report_by_arrival_detail,sale_report_by_arrival_total,financial_report,financial_report_by_sale,financial_report_by_return,financial_report_by_dzbb,logistics_report,logistics_report_by_day_delivery,logistics_report_by_io,logistics_report_by_loss'),(1005,'营销经理','A,orders,order_search,add_order,change_order_op,order_approval,manage_order,edit_order,order_detail,print_order_invoices,except_orders,C,skus,B,my_users,public_new_users,public_old_users,search_user_form,search_user,manage_users,change_user_op,change_user_type,user,edit_user,add_user,update_address,E,sale_report,sale_report_by_ygxs,sale_report_by_staff,sale_report_by_team,sale_report_by_item,sale_report_by_ygdhtj,sale_report_by_ddxsmxtj,sale_report_by_arrival_detail,sale_report_by_arrival_total,sale_report_by_return_detail,sale_report_by_return_total,financial_report,financial_report_by_sale,financial_report_by_return,financial_report_by_dzbb,financial_report_by_paidan,financial_report_by_paidan_tuihuo,financial_report_by_qianshou,financial_report_by_qianshou_tuihuo,logistics_report,logistics_report_by_day_delivery,logistics_report_by_io,logistics_report_by_loss,D,F,manage_news,edit_news,add_news,del_news,operators,edit_operator,add_operator'),(1006,'库房管理','A,orders,order_search,order_detail,C,items,skus,sku_set_manage,add_sku_set,update_sku_set_status,E,financial_report,financial_report_by_paidan,financial_report_by_paidan_tuihuo,financial_report_by_qianshou,financial_report_by_qianshou_tuihuo,logistics_report,logistics_report_by_day_delivery,logistics_report_by_wlfhhz,logistics_report_by_io,logistics_report_by_loss,D,stock_in_list,add_stock_in,edit_stock_in,stock_out_list,add_stock_out,edit_stock_out'),(1007,'媒体专员','E,analytics_report,analytics_report_by_medium,G,product_manage,medium_manage,place_manage,content_list,content_add,content_edit,ad_add,ad_list')")
        cursor.execute('COMMIT')
        cursor.execute('set FOREIGN_KEY_CHECKS = 1')
        cursor.execute('COMMIT')

        op = models.Operator()
        op.nickname = u'管理员'
        op.username = 'ai7m'
        op.password = 'ai7mecp'
        op.is_admin = True
        op.role_id = 999
        db.session.add(op)
        db.session.commit()
        print 'Init data success.'
    finally:
        _conn.close()

if __name__ == "__main__":
    manager.run()