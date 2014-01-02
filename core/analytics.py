# #coding=utf-8
# import os
# from flask import render_template,Blueprint,current_app,send_from_directory,request
#
# analytics = Blueprint('analytics',__name__,url_prefix='/analytics')
#
# @analytics.route('/ad')
# def ad():
#     return render_template('analytics/ad.html')
#
# @analytics.route('/1.gif')
# def a():
#     for k,v in request.args.iteritems():
#         print k,v
#
#     print 'remote-addr',request.remote_addr
#
#     res = send_from_directory(os.path.join(current_app.root_path, 'static/img'),'__utm.gif',mimetype='image/gif')
#     res.cache_control.no_cache=True
#     return res
#
#
