# -*- coding: utf-8 -*-
import os
from flask import Flask,render_template,request,send_from_directory,session,url_for
from wtforms import HiddenField
from extensions import db,login_manager#,principal
from core.views import admin
from core.report import report
from core.joinexport import joinexport
from core.models import Operator
from flask.ext.login import current_user

from analytics.views import analytics
#from flask.ext.principal import Principal,Identity,AnonymousIdentity,ActionNeed,RoleNeed,PermissionDenied,Permission,identity_loaded

from utils.tools import delta_s,converse_s_2_dhms_zh,des
from settings.constants import *
from datetime import datetime,timedelta
def create_app():
    _app = Flask(__name__)
    _app.config.from_pyfile('global_settings.py')
    _app.config.from_object('settings.constants')
    db.init_app(_app)


    @_app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(_app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

    configure_login(_app)
    #configure_principal(_app)
    configure_logging(_app)
    configure_jinja2(_app)
    configure_error_handlers(_app)
    _app.register_blueprint(admin)
    _app.register_blueprint(report)
    _app.register_blueprint(joinexport)
    _app.register_blueprint(analytics)
    LOGIN_MESSAGE = u'请先登录系统！'
    return _app

def configure_login(app):
    login_manager.login_view = 'admin.login'
    login_manager.login_message = u'你尚未登录 (︶︿︶)'
    #login_manager.refresh_view = 'frontend.reauth'

    @login_manager.user_loader
    def load_user(id):
        return Operator.query.get(id)
    login_manager.init_app(app)


def configure_jinja2(app):
    app.jinja_env.trim_blocks = True

    @app.template_filter()
    def is_hidden_field(field):
        return isinstance(field, HiddenField)

    @app.template_filter()
    def is_authorize(endpoint):
        return current_user.action(endpoint.rsplit('.',1)[1])

    @app.template_filter()
    def format_date(value, format='%Y.%m.%d'):
        try:
            return value.strftime(format) if value else ''
        except:
            return value

    @app.template_filter()
    def format_address(value):
        if not value or value in (u'市辖区' , u'县辖区',):
            return ''
        return value

    @app.template_filter()
    def url_link(value):
        return '<a href="'+value+'" target="_blank">'+value+'</a>' if value and value<>'http://' else ''

    @app.template_filter()
    def hide_phone(value):
        return '%s****%s'%(value[:3],value[7:]) if value else ''

    @app.template_filter()
    def default_params(key):
        return 'value="%s"'%request.args[key] if request.args.get(key,None) else ''

    @app.template_filter()
    def url_with_params(endpoint,**params):
        _params = request.args.to_dict()
        _params.update(params)
        return url_for(endpoint,**_params)

    def compare_bitwise(a,b):
        return a&b
    
    #add by john 20150409
    @app.template_filter()
    def user_token(user_id):
        return des.user_token(user_id)
    @app.template_filter()
    def user_label(user_type,order_num,label_id):
        if user_type == 1:
            if order_num>0:return u'已下单'
            return USER_LABEL_IDS.get(label_id,u'')
        return u''
    @app.template_filter()
    def type_name(user_type):
        if user_type==1:return u'新客户'
        if user_type==2:return u'会员客户'
        if user_type==4:return u'黑名单'
        if user_type==5:return u'服务客户'
    @app.template_filter()
    def assign_remain_info(assign_retain_time,assign_operator_id,order_num,assign_time):
        if assign_operator_id and assign_retain_time>0 and order_num==0:
            expired = assign_time+timedelta(hours=assign_retain_time)
            now = datetime.now()
            return converse_s_2_dhms_zh(delta_s(expired,now)) if expired>now else u'已到期'
        return '-'











    app.jinja_env.globals.update(compare_bitwise=compare_bitwise)


def configure_logging(app):
    """Configure file(info) and email(error) logging."""
    import logging
    from logging.handlers import SMTPHandler

    app.logger.setLevel(logging.INFO)
    file_handler = logging.handlers.RotatingFileHandler(os.path.join(app.config['LOG_PATH'], 'ecp.log'), maxBytes=100000, backupCount=10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s](%(levelname)s) %(message)s  [%(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)

    # ADMINS = ['sindon@gmail.com']
    # mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
    #     app.config['MAIL_USERNAME'],
    #     ADMINS,
    #     'O_ops... %s failed!' % app.config['PROJECT'],
    #     (app.config['MAIL_USERNAME'],
    #      app.config['MAIL_PASSWORD']))
    # mail_handler.setLevel(logging.ERROR)
    # mail_handler.setFormatter(logging.Formatter(
    #     '%(asctime)s %(levelname)s: %(message)s '
    #     '[in %(pathname)s:%(lineno)d]')
    # )
    # app.logger.addHandler(mail_handler)

def configure_error_handlers(app):
   @app.errorhandler(403)
   def forbidden_page(error):
       return render_template("errors/forbidden_page.html"), 403

   @app.errorhandler(404)
   def page_not_found(error):
       return render_template("errors/page_not_found.html"), 404

   @app.errorhandler(500)
   def server_error_page(error):
       return render_template("errors/server_error.html"), 500