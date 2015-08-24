#coding=utf-8

#库房配置表
STORES = {
    1:u'成都仓',
    2:u'北京仓',
    3:u'西安仓',
    }
STORES2 = {
    0:u'无',
    1:u'成都仓',
    2:u'北京仓',
    3:u'西安仓',
    }


#快递公司配置
EXPRESS_CONFIG = {
    1:{'name':u'成都顺丰','code':'shunfeng','stores':[1,2],'area_url':'http://www.sf-express.com/cn/sc/delivery_step/enquiry/coverageArea.html'},
    2:{'name':u'宅急送','code':'zhaijisong','stores':[1],'area_url':'http://www.zjs.com.cn/WS_Business/WS_Bussiness_CityArea.aspx?id=6'},
    3:{'name':u'飞狐快递','code':'feihukuaidi','stores':[1],'area_url':''},
    4:{'name':u'优速快递','code':'yskd','stores':[1],'area_url':'http://www.uc56.com/Chinese/RagionSearchMsg.aspx'},
    5:{'name':u'邮政小包','code':'youzhengguonei','stores':[1],'area_url':'http://www.ems.com.cn/'},
    6:{'name':u'邮政快递','code':'youzhengguonei','stores':[1],'area_url':'http://www.ems.com.cn/'},
    7:{'name':u'北京飞狐','code':'feihukuaidi','area_url':'','stores':[2]},
    8:{'name':u'申通快递','code':'shentong','stores':[1],'area_url':'http://www.sto.cn/web%20select.asp'},
    9:{'name':u'陆航韵达','code':'luhangyunda','area_url':'','stores':[1]},
    10:{'name':u'EMS','code':'ems','area_url':'','stores':[3]},
    11:{'name':u'西安顺丰','code':'shunfeng','stores':[3],'area_url':'http://www.sf-express.com/cn/sc/delivery_step/enquiry/coverageArea.html'},
    12:{'name':u'百世汇通','code':'htky','stores':[3],'area_url':'http://www.htky365.com/Site/Query'},
    99:{'name':u'客户自提','code':'kfzq','area_url':'','stores':[1,2,3]}
}

LOSS_TYPES = {
    1:u'订单',
    2:u'人工'
}

LOSS_CHANNELS = {
    1:u'不明原因',
    2:u'原厂损坏',
    3:u'库房损坏',
    4:u'发货途中',
    5:u'退货途中',
}

LOSS_DEGREES={
    1:u'其他',
    2:u'发霉',
    3:u'外包装损',
    4:u'破碎'
}

LOSS_STATUS = {
    0:u'全部',
    1:u'未审核',
    2:u'待审核',
    9:u'正常'
}

#订单状态配置
ORDER_STATUS = {
    0:u'所有状态',
    1:u'待员工审核',
    2:u'待内勤审核',
    3:u'待财务审核',
    40:u'待拣货',
    4:u'待发货',
    5:u'已发货',
    6:u'已到货',
    60:u'待财务确认',
    7:u'待退货审核',
    8:u'待退款审核',

    9:u'拒收退货确认',
    10:u'失败返货',
    11:u'投递失败',
    12:u'退货重发申请',
    13:u'退货退款申请',
    14:u'投递失败待退款',

    31:u'待退货审核',
    32:u'待退货入库确认',
    33:u'退货待处理',
    34:u'申请换货中',
    35:u'申请退款中',
    36:u'退货待退款',

    51:u'退款待确认',

    100:u'已完成',
    101:u'已拒收',
    102:u'已退货',
    103:u'已作废',
    104:u'拒收已退货',
    105:u'投递失败已重发',
    106:u'投递失败已退款',
    107:u'换货已重发',
    108:u'已退款',
    109:u'已退款',
    }


#用户标签类型
USER_LABEL_IDS = {
    1:u'未下单',
    2:u'下单拒收',
    3:u'下单退货',
    4:u'下单作废',
}

#订单状态关联用户标签
ORDER_STATUS_RELATED_USER_LABEL = {
    101:2,102:3,103:4,104:2,105:2,106:2,107:2,108:2
}


#显示退货明细状态
ORDER_DISPLAY_RETURN_STATUS = (8,33,34,35,36,11,12,13,14,101,102,103,104,105,106,107,108)

#允许重发订单状态
ORDER_ALLOWED_RETRAN_STATUS = (104,105,107)

#订单允许编辑状态列表
ORDER_ALLOWED_EDIT_STATUS = (1,)

#订单允许修改地址状态
ORDER_ALLOWED_ADDRESS_STATUS = (1,)

# #订单允许编辑物流状态
# ORDER_ALLOWED_EXPRESS_STATUS = (4,)

USER_ROLE = {
    0:u'系统管理员',
    1:u'员工',
    2:u'销售内勤',
    4:u'财务',
    8:u'物流',
    9:u'物流内勤',
    16:u'销售主管',
    32:u'产品管理',
    }

#角色允许操作订单状态
ROLE_ALLOWED_ORDER_STATUS = {
    101:[1,5,11,33,100,105,107],
    102:[2],
    103:[3,60,36,14,51],
    104:[4,32,9,10,40],
    105:[6],
    106:[31,34,35,12,13],
    }

#下单角色ID
ORDER_ROLE_ID = 101
SEE_ORDER_ROLE_ID = [101,106,1000,1001,1002,1003,1005]

#订单审批流程配置[操作,界面样式,变更状态,付款方式,库存标识(0:无,1:出库,2:入库)]
ORDER_OPROVRAL_CONFIG = {
    1:[(u'员工确认','btn-success',2,3,0),(u'订单作废','btn-warning',103,3,0),(u'申请退款','btn-danger',51,2,0)],#员工
    2:[(u'内勤确认','btn-success',40,1,0),(u'内勤确认','btn-success',3,2,0),(u'打回订单','btn-warning',1,3,0)],#内勤
    3:[(u'财务确认','btn-success',40,3,0),(u'打回订单','btn-warning',1,3,0)],#财务
    40:[(u'拣货完成','btn-success',4,3,0),(u'打回订单','btn-warning',1,3,0)],
    4:[(u'确认发货','btn-success',5,3,1),(u'打回订单','btn-warning',1,3,0)],#物流
    5:[(u'到货确认','btn-success',6,1,0),(u'客户拒收','btn-warning',9,1,0),(u'到货确认','btn-success',100,2,0),(u'投递失败','btn-warning',10,2,0)],#员工
    6:[(u'对账确认','btn-success',60,1,0),(u'退回发货','btn-warning',5,1,0)],#物流内勤
    60:[(u'财务确认','btn-success',100,1,0),(u'退回对账','btn-warning',6,1,0)],#财务
    #7:[(u'退货确认','btn-danger',8,3,2)],

    31:[(u'退货确认','btn-success',32,3,0),(u'打回申请','btn-warning',100,3,0)],#销售主管
    32:[(u'入库确认','btn-success',33,3,2)],#物流
    33:[(u'申请换货','btn-warning',34,3,0),(u'申请退款','btn-danger',35,3,0)],#员工
    34:[(u'换货确认','btn-success',107,3,0),(u'打回申请','btn-warning',33,3,0)],#销售主管
    35:[(u'批准退款','btn-success',36,3,0),(u'打回申请','btn-warning',33,3,0)],#销售主管
    36:[(u'退款确认','btn-danger',108,3,0)],#财务

    51:[(u'退款确认','btn-danger',109,2,0),(u'打回订单','btn-warning',1,2,0)],#财务


    #8:[(u'退款确认','btn-danger',102,3,0)],
    9:[(u'入库确认','btn-danger',104,1,2),(u'退回发货','btn-warning',5,1,0)],#物流
    10:[(u'入库确认','btn-danger',11,2,2)],#物流
    11:[(u'申请重发','btn-warning',12,2,0),(u'申请退款','btn-danger',13,2,0)],#员工
    12:[(u'批准重发','btn-success',105,2,0),(u'退回申请','btn-warning',11,2,0)],#销售主管
    13:[(u'批准退款','btn-success',14,2,0),(u'退回申请','btn-warning',11,2,0)],#销售主管
    14:[(u'退款确认','btn-danger',106,3,0)],#财务
    100:[(u'申请退货','btn-warning',31,3,0)]#员工
}



#模块列表
MODULES = {
    'A':u'订单管理',
    'B':u'客户管理',
    'C':u'商品管理',
    'D':u'仓储管理',
    'E':u'统计报表',
    'F':u'系统管理',
    'G':u'广告管理',
    'H':u'防伪码管理',
    'I':u'知识管理',
    'J':u'报表系统',
}

#权限节点列表（节点,名称,所属模块）
ENDPOINTS = [
    ('orders',u'订单查询','A'),
    ('order_search',u'订单检索','A'),
    ('add_order',u'订单录入','A'),
    ('sf_order',u'快递单生成','A'),
    ('print_sf',u'打印顺风','A'),
    ('change_order_op',u'订单转派','A'),
    ('order_approval',u'待处理订单','A'),
    ('manage_order',u'订单审批','A'),
    ('edit_order',u'订单编辑','A'),
    ('order_detail',u'查看订单','A'),
    ('print_order_invoices',u'发货单打印','A'),
    ('order_fast_delivery',u'一键发货','A'),
    ('order_fast_delivery_detal',u'一键发货明细','A'),
    ('order_retransmission',u'重发订单','A'),
    ('order_repeatinsku',u'重复入库','A'),
    ('except_orders',u'差额订单调整','A'),
    ('order_lhyd_yz',u'陆航韵达邮政录单','A'),
    ('hasarrived',u'一键物流对帐','A'),
    ('caiwuqr',u'一键财务对帐','A'),
    ('getuserinfobyeid',u'快递单查归属','A'),
    ('clear_order_items',u'订单缓存','A'),

    ('my_users',u'我的客户库','B'),
    ('public_new_users',u'新客户公共库','B'),
    ('public_old_users',u'会员公共库','B'),
    ('public_service_users',u'服务公共库','B'),
    ('public_servicelz_users',u'服务流转公共库','B'),
    ('qxhdm_users',u'地面公共库','B'),
    ('search_user_form',u'客户检索输入框','B'),
    ('search_user',u'客户检索','B'),
    ('giveup_users',u'放弃客户审核','B'),
    ('giveup_user_ok',u'放弃客户通过审核','B'),
    ('giveup_user_no',u'放弃客户不通过审核','B'),
    ('giveup_user_sq',u'我申请的放弃客户','B'),
    ('giveup_user_audit',u'我审核的放弃客户','B'),
    ('servicetype_users',u'停用启用客户审核','B'),
    ('servicetype_user_ok',u'停用启用客户通过审核','B'),
    ('servicetype_user_no',u'停用启用客户不通过审核','B'),
    ('servicetype_user_sq',u'我申请的停用启用客户','B'),
    ('servicetype_user_audit',u'我审核的停用启用客户','B'),

    ('manage_users',u'客户管理','B'),
    ('change_user_op',u'变更客户归属','B'),
    ('change_user_type',u'变更客户类型','B'),
    ('user',u'查看客户','B'),
    ('edit_user',u'编辑客户','B'),
    ('add_user',u'新增客户','B'),
    ('update_address',u'客户地址更新','B'),
    ('view_user_phone',u'查看客户号码','B'),
    ('sms_list',u'短信查询','B'),
    ('sms_approval',u'短信审批','B'),
    ('sms_mass',u'短信群发','B'),
    ('sale_user_list',u'会员客户统计','B'),
    ('search_knowledge',u'知识查询','B'),
    ('voucheradd',u'添加代金卷','B'),
    ('scratch',u'刮刮卡登记','B'),
    ('scratchdjqx',u'刮刮卡删除','B'),

    ('khsldel',u'删除空盒送礼','B'),
    ('fgypdel',u'删除复购预判','B'),
    ('tjfgdel',u'删除推荐复购','B'),
    ('savedlb_user',u'增加大礼包','B'),
    ('integration_list',u'积分管理','B'),
    ('integration_edit',u'积分增加','B'),





    ('items',u'商品管理','C'),
    ('del_item',u'删除商品','C'),
    ('skus',u'SKU查询','C'),
    ('edit_sku',u'SKU编辑','C'),
    ('add_sku',u'SKU添加','C'),
    ('sku_set_manage',u'套餐查询','C'),
    ('add_sku_set',u'添加套餐','C'),
    ('update_sku_set_status',u'套餐审批','C'),

    # ('stocks',u'库存查询','D'),
    # ('add_stock',u'入库登记','D'),
    # ('edit_stock',u'库存编辑','D'),
    # ('stock_approval',u'入库审批','D'),
    # ('losses',u'报损查询','D'),
    # ('loss_approval',u'报损审批','D'),
    # ('add_loss',u'报损登记','D'),
    ('purchase_price',u'查看进货价','D'),
    ('stock_in_list',u'入库查询','D'),
    ('stock_in_approval',u'入库审批','D'),
    ('add_stock_in',u'入库登记','D'),
    ('edit_stock_in',u'编辑入库','D'),
    ('stock_out_list',u'出库查询','D'),
    ('stock_out_approval',u'出库审批','D'),
    ('add_stock_out',u'出库登记','D'),
    ('edit_stock_out',u'编辑出库','D'),
    ('stock_delete',u'删除库存登记','D'),

    ('sale_report',u'营销报表','E'),
    ('sale_report_by_ygxs',u'[营销]员工产品销售统计','E'),
    ('sale_report_by_staff',u'[营销]员工销售统计','E'),
    ('sale_report_by_team',u'[营销]部门销售统计','E'),
    ('sale_report_by_item',u'[营销]产品销售统计','E'),
    ('sale_report_by_ygdhtj',u'[营销]员工产品到货统计','E'),
    ('sale_report_by_ddxsmxtj',u'[营销]订单销售明细统计','E'),
    ('sale_report_by_arrival_detail',u'[营销]到货明细表','E'),
    ('sale_report_by_arrival_total',u'[营销]到货汇总表','E'),
    ('sale_report_by_return_detail','[营销]退货明细表','E'),
    ('sale_report_by_return_total','[营销]退货汇总表','E'),
    ('sale_report_by_user_total','[营销]会员客户数量统计','E'),
    ('sale_report_user_list',u'[营销]会员客户详细','E'),
    ('jiexian_tongji',u'[营销]外呼统计','E'),
    ('xlj_sale_tongji',u'[营销]心力健销售统计','E'),
    ('xlj_mtjxqk',u'[营销]心力健媒体进线情况表','E'),
    ('xlj_xsqkb',u'[营销]心力健销售情况表','E'),
    ('yy_khsl',u'[营销]空盒送礼登记表','E'),
    ('yy_fgtj',u'[营销]复购统计','E'),
    ('sale_scratchjx',u'[营销]刮刮卡进线','E'),
    ('sale_scratchqyjx',u'[营销]刮刮卡区域进线','E'),
    ('sale_scratchmx',u'[营销]刮刮卡明细','E'),


    ('financial_report',u'财务报表','E'),
    ('financial_report_by_sale',u'[财务]日销售明细表','E'),
    ('financial_report_by_return',u'[财务]日退货明细表','E'),
    ('financial_report_by_dzbb',u'[财务]对账报表','E'),
    ('financial_report_by_dzbbmx',u'[财务]对账明细报表','E'),
    ('financial_report_by_paidan',u'[财务]物流派单表','E'),
    ('financial_report_by_paidantongji',u'[财务]物流派单表统计','E'),
    ('financial_report_by_paidan_tuihuo',u'[财务]物流派单退货表','E'),
    ('financial_report_by_paidantuihuotongji',u'[财务]物流派单退货表统计','E'),
    ('financial_report_by_qianshou',u'[财务]物流签收表','E'),
    ('financial_report_by_qianshoutongji',u'[财务]物流签收表统计','E'),
    ('financial_report_by_qianshou_tuihuo',u'[财务]物流签收退货表','E'),
    ('financial_report_by_paidan_zaitu',u'[财务]物流派单在途明细表','E'),
    ('financial_report_by_paidan_dzzaitu',u'[财务]物流派单对帐在途明细表','E'),
    ('financial_report_by_paidan_pdwdz',u'[财务]物流派单未对帐明细表','E'),

    ('logistics_report',u'物流报表','E'),
    ('logistics_report_by_day_delivery',u'[物流]物流发货明细表','E'),
    ('logistics_report_by_wlfhhz',u'[物流]物流发货汇总表','E'),
    ('logistics_report_by_io',u'[物流]商品出入库明细表','E'),
    ('logistics_report_by_loss',u'[物流]报损汇总表','E'),

    ('pharmacy_report',u'药房报表','E'),
    ('pharmacy_report_by_shuju',u'[药房]数据录入统计 ','E'),
    ('pharmacy_report_by_shujufankui',u'[药房]数据反馈统计','E'),
    ('pharmacy_report_by_fugou',u'[药房]复购统计报表','E'),
    ('pharmacy_report_by_fugouypmx',u'[药房]复购预判明细统计','E'),
    ('pharmacy_report_by_khfgypmx',u'[药房]服务组复购预判明细表','E'),
    ('pharmacy_report_by_khfwmx',u'[药房]空盒换大礼服务明细表 ','E'),

    ('dlb_report',u'大礼包报表','E'),
    ('dlb_zt',u'[大礼包]整体进线情况表 ','E'),
    ('dlb_new',u'[大礼包]新客户处理情况表','E'),
    ('dlb_jinxian',u'[大礼包]进线类型统计表','E'),
    
    ('servicelz_report',u'服务流转报表','E'),
    ('servicelz_report_mx',u'[服务流转]服务流转数据明细表 ','E'),
    ('servicelz_report_tj',u'[服务流转]服务流转数据统计表','E'),



    ('waihu_report',u'外呼报表','J'),
    ('waihu_report1',u'[外呼]持有数据量 ','J'),
    ('waihu_report2',u'[外呼]接线流转数据业绩','J'),
    ('waihu_report3',u'[外呼]TQ流转数据业绩','J'),
    ('waihu_report4',u'[外呼]其他流转数据业绩','J'),
    ('waihu_report5',u'[外呼]外呼报表','J'),

    ('fuwu_report',u'服务报表','J'),
    ('fuwu_report1',u'[外呼]服务报表 ','J'),
    ('fuwu_report2',u'[外呼]维护数据','J'),

    ('weihu_report',u'维护报表','J'),
    ('weihu_report1',u'[维护]数据报表一 ','J'),
    ('weihu_report2',u'[维护]数据报表二','J'),
    ('weihu_reportyeji',u'[维护]业绩报表','J'),
    ('weihu_reportcpgc',u'[维护]产品构成','J'),

    ('jiexian_report',u'接线报表','J'),
    ('jiexian_report1',u'[接线]业绩报表 ','J'),
    ('jiexian_report2',u'[接线]接线报表','J'),

    ('analytics_report',u'广告统计','E'),
    ('analytics_report_by_medium',u'媒体广告统计','E'),

    ('product_manage',u'产品管理','G'),
    ('medium_manage',u'媒体管理','G'),
    ('place_manage',u'广告位管理','G'),
    ('content_list',u'广告内容管理','G'),
    ('content_add',u'添加广告内容','G'),
    ('content_edit',u'修改广告内容','G'),
    ('ad_add',u'添加广告','G'),
    ('ad_list',u'查看广告列表','G'),

    ('manage_news',u'公告管理','F'),
    ('edit_news',u'公告编辑','F'),
    ('add_news',u'公告添加','F'),
    ('del_news',u'公告删除','F'),
    ('operators',u'操作员查询','F'),
    ('edit_operator',u'修改操作员','F'),
    ('add_operator',u'添加操作员','F'),
    ('del_operator',u'删除操作员','F'),
    ('roles',u'角色管理','F'),
    ('manage_role',u'权限编辑','F'),
    
    
    ('securitycodes',u'防伪码查询','H'),
    ('securitycodelog',u'防伪码查询记录','H'),
    ('securitycode_khbmcx',u'空盒编码查询','H'),
    ('securitycode_scratch',u'刮刮卡编码查询','H'),

    ('categorys',u'知识类别管理','I'),
    ('manage_knowledge',u'知识管理','I'),
    ('edit_knowledge',u'知识编辑','I'),
    ('add_knowledge',u'知识添加','I'),
    ('del_knowledge',u'知识删除','I'),

]

ITEM_CATEGORYS = {
    1:u'保健品',
    2:u'护肤品',
    3:u'药品',
    9:u'赠品'
}

SKU_PROPERTIES = ['p1','p2','p3']
SKU_PROPERTIES_NAME = {'p1':u'规格','p3':u'剂型','p2':u'单位'}


ORDER_TYPES = {
    1:u'客服订单',
    2:u'会员订单',
    3:u'代理商订单',
    4:u'团购订单',
    5:u'内部订购',
    6:u'渠道商订单',
    7:u'网店订单',
    8:u'网上订单',
    9:u'TQ订单',
    10:u'留言订单',
    11:u'淘宝订单',
    12:u'亚马逊订单',
    13:u'天猫订单',
    14:u'心力健送书订单',
    15:u'心力健成交订单',
    16:u'心力健复购订单',
    17:u'会员服务订单',
    18:u'大礼包订单',
    19:u'PPTV订单',
    101:u'样品订单',
    102:u'客情订单',
    103:u'调库订单',
    104:u'抽奖活动订单',
    }
USED_ORDER_TYPES = [1,9,2,17,8,19,18,10,13,5,101,102,103,104]
ORDER_RELATED_STOCK_OUT_CATEGORIES = {
    101:14,102:13,103:12
}

ORDER_MODES = {
    1:u'接线呼出',
    2:u'外呼呼出',
    3:u'电话呼入',
    4:u'会员维护',
    5:u'留言呼出',
    6:u'渠道商进货',
    7:u'在线咨询',
    8:u'刮刮卡',
    9:u'试纸',
    10:u'淘宝订单',
    11:u'天猫订单',
    12:u'药房网订单',
    13:u'亚马逊订单',
    14:u'立方网网上订单',
    15:u'爱妻美网上订单',
    16:u'心力健',
    17:u'会员服务活动',
    18:u'大礼包送礼',
    19:u'大礼包送礼订购',
    20:u'大礼包到礼订购',
    21:u'PPTV送礼',
    22:u'PPTV送礼订购',
    23:u'PPTV到礼订购',
    24:u'官网注册',
    25:u'刮刮卡送礼',
    100:u'其它',
}
USED_ORDER_MODES = [3,1,2,5,7,4,17,25,18,19,20,21,22,23,9,11,14,15,24,100]
ORDER_PAYMENTS = {
    1:u'货到付款',
    2:u'先款后货',
}

AREA = {
    u'山东':u'山东',
    u'四川':u'四川',
    u'黑龙江':u'黑龙江',
    u'陕西':u'陕西',
    u'广东':u'广东',
    u'四川成都':u'四川成都',
    u'四川二级':u'四川二级',
    u'北京':u'北京',
    u'天津':u'天津',
    u'上海':u'上海',
    u'重庆':u'重庆',
    u'河北':u'河北',
    u'山西':u'山西',
    u'辽宁':u'辽宁',
    u'吉林':u'吉林',
    u'江苏':u'江苏',
    u'浙江':u'浙江',
    u'安徽':u'安徽',
    u'福建':u'福建',
    u'江西':u'江西',
    u'河南':u'河南',
    u'湖北':u'湖北',
    u'湖南':u'湖南',
    u'海南':u'海南',
    u'贵州':u'贵州',
    u'云南':u'云南',
    u'甘肃':u'甘肃',
    u'青海':u'青海',
    u'台湾':u'台湾',
    u'广西':u'广西',
    u'内蒙古':u'内蒙古',
    u'西藏':u'西藏',
    u'宁夏':u'宁夏',
    u'新疆':u'新疆',
    u'澳门':u'澳门',
    u'香港':u'香港',

}
COMMUNICATIONS={
    u'接通':u'接通',
    u'未联系上':u'未联系上',
    u'想换四件套':u'想换四件套',
    u'放弃':u'放弃',
    u'嫌麻烦不登记':u'嫌麻烦不登记',
    u'不是本人电话':u'不是本人电话',
}
ISABLEREASONS={
    u'两次不能联系本人':u'两次不能联系本人',
    u'两次客户说不用指导':u'两次客户说不用指导',
    u'连续六次未能联系':u'连续六次未能联系',
    u'送朋友':u'送朋友',
    u'药房电话':u'药房电话',
}

USER_ORIGINS = {
    1:u'接线',
    2:u'外呼',
    3:u'商城',
    4:u'TQ',
    5:u'会员推荐',
    6:u'分销商',
    27:u'刮刮卡2015',
    7:u'刮刮卡',
    8:u'试纸',
    9:u'聚美',
    10:u'外呼放弃',
    11:u'心力健',
    12:u'气血和601',
    13:u'地面已购',
    14:u'抽奖未购',
    15:u'抽奖已购',
    16:u'维护老顾客抽奖',
    17:u'终端微信',
    18:u'终端提交',
    19:u'空盒换大礼',
    20:u'防伪码管理',
    21:u'促销',
    22:u'核销',
    23:u'流转',
    24:u'漏接',
    25:u'微信150527',
    26:u'官网注册',
    99:u'其它',
}
USED_USER_ORIGINS = [1,20,27,19,26,2,4,5,8,10,18,23,24,99]
NEED_PAID_USER_ORIGINS = [7,8,9,11,13]

#操作员分配客户时长(根据来源)
USER_ASSIGN_HOURS = {
    1:72,2:168,3:72,4:168,5:72,6:72,7:1440,8:1440,9:1440,13:5,99:1440
}

ASSIGN_DEFAULT_HOURS = 72

USER_INTENT_LEVELS = ['A','B','C','D','E','F','G','H','I']

USER_STATUS = {
    0:u'全部',
    1:u'正常',
    2:u'冻结',
    3:u'作废',
    9:u'待分配'
}

USER_SORT_NAMES = [
    ('last_dialog_time',u'最后联系日期'),
    ('dialog_times',u'联系次数'),
    ('join_time',u'创建日期'),
    ('expect_time',u'预约时间'),
    ('assign_time',u'分配时间'),
]

SORT_SCS = [
    (0,u'顺序'),
    (1,u'倒序'),
    ]

DISCOUNT_TYPES = {
    0:u'无折扣',
    1:u'普通会员',
    2:u'银卡会员',
    3:u'金卡会员',
    4:u'商品促销优惠'
}

STOCK_STATUS = {
    1:u'审批未通过',
    2:u'待审批',
    9:u'正常'
}

STOCK_IN_CATEGORIES = {
    10:u'采购入库',
    11:u'借调入库',
    12:u'调库入库',
    19:u'历史入库',
    20:u'退货入库',
    21:u'系统重发入库'
}

STOCK_IN_CATEGORIES_IDs = [10,11,12,19,21]

STOCK_OUT_CATEGORIES = {
    10:u'销售出库',
    11:u'借调出库',
    12:u'调库出库',
    13:u'客情出库',
    14:u'样品出库',
    15:u'系统重入出库',
    20:u'报损出库',
    21:u'奖品出库'
}

STOCK_OUT_CATEGORIES_IDs = [12,13,14,15,20,11,21]

#商品最小允许订购数量
ITEM_QUANTITY_THRESHOLD = 200

#SKU单位
SKU_UNITS = [u'件',u'盒',u'瓶',u'袋',u'个',u'套',u'本',u'条',u'张']

#操作员状态
OPERATOR_STATUS = {
    1:u'上班',
    2:u'下班',
    9:u'冻结'
}

#操作员允许分配客户类型
OPEARTOR_ASSIGN_USER_TYPES = {
    0:u'无',
    1:u'新客户',
    2:u'会员客户',
    5:u'会员服务',
    6:u'服务流转',
    #3:u'新客户+会员客户'
}

#客户类型
USER_TYPES = {
    1:u'新客户',
    2:u'会员客户',
    5:u'会员服务',
    6:u'服务流转',
    4:u'黑名单',
}




DEPARTMENTS = {
    'A':u'接线部',
    'B':u'外呼部',
    'C':u'维护部',
    'D':u'分销商',
    'K':u'客情',
    'E':u'第三方商城'
}


TEAMS = {
    '':u'无',
    'A1':u'芪枣组',
    'A2':u'爱妻美组',
    'B1':u'外呼组',
    'B2':u'TQ组',
    'B3':u'心力健1组',
    'B4':u'心力健2组',
    'C1':u'维护1组',
    'C2':u'维护2组',
    'C3':u'服务组',
    'D1':u'分销商',
    'K1':u'客情',
    'E1':u'淘宝',
    'E2':u'京东',
    'E3':u'亚马逊'
}

TEAM_RETAIN_USER_HOURS = {
    'A1':{0:72,13:1},
    'A2':{0:72,13:1},
    #'B1':{0:720,7:1440,8:1440,9:1440},
    #'B2':{0:720,7:1440,8:1440,9:1440},
    #'B3':{0:720},
    #'B4':{0:720},
    'B1':{0:2160},
    'B2':{0:2160},
    'B3':{0:2160},
    'B4':{0:2160},
    'C1':{0:0},
    'C2':{0:0},
    'C3':{0:0},
    'D1':{0:0},
    'K1':{0:0},
    'E1':{0:72},
    'E2':{0:72},
    'E3':{0:72}
}

TEAM_RETAIN_DEFAULT_HOURS = 72


################
DIALOG_TYPES = {
    0:u'产品咨询',
    1:u'到货情况',
    2:u'服用情况',
    3:u'再次订购',
    4:u'销售跟进',
    5:u'生日问候',
    6:u'节日问候',
    99:u'未定义',
}


#客户身体字段配置（编码,名称,字段类型(0:输入框)）
USER_BODY_CONFIG = [
    ['A',u'五官',[('A01',u'眼',1),
                ('A02',u'耳',1),
                ('A03',u'鼻',1),
                ('A04',u'喉',1),
                ('A05',u'齿',1),
                ('A06',u'舌',1),
                ('A07',u'牙',1),
                ('A08',u'头',1),
                ('A09',u'发',1),
                ('A10',u'面',1)],
     'label label-info',
    ],
    ['B',u'脏器',[('B01',u'心',1),
                ('B02',u'肝',1),
                ('B03',u'脾',1),
                ('B04',u'肺',1),
                ('B05',u'肾',1),
                ('B06',u'胰',1),
                ('B07',u'子宫',1),
                ('B08',u'卵巢',1),
                ('B09',u'膀胱',1),
                ('B10',u'前列腺',1),
                ('B11',u'胸',1),
                ('B12',u'胃',1),
                ('B13',u'肛肠',1)],
     'label label-info',
    ],
    ['C',u'四肢',[('C01',u'手',1),
                ('C02',u'脚',1),
                ('C03',u'关节',1),
                ('C04',u'颈',1),
                ('C05',u'肩',1),
                ('C06',u'胸腰',1),
                ('C07',u'尾椎',1)],
     'label label-info',
    ],
    ['D',u'心脑血管',[('D01',u'大脑',1),
                ('D02',u'心脏',1),
                ('D03',u'血管',1)],
     'label label-info',
    ],
    ['E',u'神经',[('E01',u'失眠',0),
                ('E02',u'抑郁',0),
                ('E03',u'风湿',0),
                ('E04',u'过敏史',0)],
     'label label-info',
    ],
    ['Z',u'病症',[('Z01',u'病史',1)],
     'label label-warning',
    ],
    ]
#器官
USER_ORGIN = {
    'A':u'五官',
    'B':u'脏器',
    'C':u'四肢',
    'D':u'心脑血管',
    'E':u'神经',
}
#器官列表（节点,名称,所属模块）
USER_ORGIN_SUB = {
    
    'A01':u'眼',
    'A02':u'耳',
    'A03':u'鼻',
    'A04':u'喉',
    'A05':u'齿',
    'A06':u'舌',
    'A07':u'牙',
    'A08':u'头',
    'A09':u'发',
    'A10':u'面',
    
    'B01':u'心',
    'B02':u'肝',
    'B03':u'脾',
    'B04':u'肺',
    'B05':u'肾',
    'B06':u'胰',
    'B07':u'子宫',
    'B08':u'卵巢',
    'B09':u'膀胱',
    'B10':u'前列腺',
    'B11':u'胸',
    'B12':u'胃',
    'B13':u'肛肠',
    
    'C01':u'手',
    'C02':u'脚',
    'C03':u'关节',
    'C04':u'颈',
    'C05':u'肩',
    'C06':u'胸腰',
    'C07':u'尾椎',
    
    'D01':u'大脑',
    'D02':u'心脏',
    'D03':u'血管',
    
    'E01':u'失眠',
    'E02':u'抑郁',
    'E03':u'风湿',
    'E04':u'过敏史'
    
}

#客户生活习惯字段配置
USER_LIFE_CONFIG = [
    ['F',u'饮食习惯',[('F01',u'辛辣',0),
                ('F02',u'咸',0),
                ('F03',u'清淡',0),
                ('F04',u'正常',0),
                ],
    'label',
    ],
    ['G',u'运动习惯',[('G01',u'规律',0),
                  ('G02',u'很少',0),
                  ('G03',u'不定期',0),
                  ],
    'label',
     ],
    ['H',u'睡眠习惯',[('H01',u'早睡',0),
                  ('H02',u'晚睡',0),
                  ('H03',u'正常',0)
                  ],
     'label',
     ],
]

#用户收入配置
USER_INCOME_CONFIG = {
    0:u'保密',
    1:u'2万以下',
    2:u'2万～5万',
    3:u'5万～10万',
    4:u'10万～15万',
    5:u'15万～20万',
    6:u'20万～30万',
    7:u'30万～50万',
    8:u'50万以上'
}

#用户行业配置表
USER_PROFESSION_CONFIG = {
    'A':u'农、林、牧、渔业',
    'B':u'采矿业',
    'C':u'制造业',
    'D':u'电力、热力、燃气及水生产和供应业',
    'E':u'建筑业',
    'F':u'批发和零售业',
    'G':u'交通运输、仓储和邮政业	',
    'H':u'住宿和餐饮业',
    'I':u'信息传输、软件和信息技术服务业',
    'J':u'金融业',
    'K':u'房地产业',
    'L':u'租赁和商务服务业',
    'M':u'科学研究和技术服务业',
    'N':u'水利、环境和公共设施管理业',
    'O':u'居民服务、修理和其他服务业',
    'P':u'教育',
    'Q':u'卫生和社会工作',
    'R':u'文化、体育和娱乐业',
    'S':u'公共管理、社会保障和社会组织',
    'T':u'国际组织'
}


USER_AGES = {
    0:u'保密',
    1:u'20岁以下',
    2:u'20岁～30岁',
    3:u'30岁～40岁',
    4:u'40岁～50岁',
    5:u'50岁以上',
}


CONCERNS = {
    'A':u'效果',
    'B':u'信任度',
    'C':u'产品品质',
    'D':u'售后服务',
    'E':u'价格'
}


SMS_STATUS = {
    0:u'待审批',
    1:u'待发送',
    2:u'发送成功',
    9:u'发送失败'
}


PRODUCT_INTENTION = {
    0:u'气血和胶囊',
    1:u'芪枣健胃茶',
    2:u'保健品',
    3:u'化妆品',
    5:u'心力健',
    6:u'心力健其它',
    7:u'新会员',
    8:u'大礼包',
    9:u'PPTV',
    4:u'其它'
}
#心力健媒体
XLJ_MEDIA = {
    1:u'心力健老年生活报',
    2:u'心力健江南保健报',
    3:u'心力健快乐老人报（山东）',
    4:u'心力健长沙晚报',
    5:u'心力健扬州晚报',
    6:u'心力健福建老年报',
    7:u'心力健厦门晚报',
    8:u'心力健楚天都市报',
    9:u'心力健北京晨报',
    10:u'心力健扬子晚报',
    11:u'心力健新安晚报',
    12:u'心力健燕赵晚报',
    13:u'心力健青岛早报',
    14:u'心力健全国|老年日报',
    15:u'心力健全国|快乐老人报',
    16:u'心力健全国|中国老年报',
    17:u'心力健全国|文摘周刊',
    18:u'心力健全国|家庭医生',
    19:u'心力健全国|文萃报'
}

#微信情况
WEIXINS = {
    'A':u'没有微信',
    'B':u'有微信，没关注气血和',
    'C':u'已关注气血和官微',
    'D':u'已关注医师微信',
    'E':u'空缺',
}
#大礼包类型
DLB_TYPES = {
    1:u'留言',
    2:u'微信',
    3:u'PPTV',
}
DLB_ROLES = [1005,106]
DLB_ROLESS = [1005,106,102]

XLJ_ID = 10125

DRUGS = '10001,10002,10003,10004,10120,'#药品ID

INTEGRATION_STATUS = {
    1:u'官网注册',
    2:u'订单消耗',
    3:u'订单增加',
    4:u'手动增加',
    5:u'2015年1-6月到货金额增加',
    6:u'2015年1-6月退货金额减少'
}

from global_settings import SF_D
from global_settings import SF_Custid
from global_settings import SF_Key
from global_settings import SF_Url

from global_settings import KF_ROOLEIDS
from global_settings import KF_XIANID
from global_settings import KF_CHENGDUID
from global_settings import WLNQ_XIANID
from global_settings import WLNQ_CHENGDUID



from global_settings import ITEM_CACHE
ALLOWED_ORDER_ITEMS_CACHE_KEY = 'ORDER_ITEMS_CACHE_KEY_%s'%ITEM_CACHE