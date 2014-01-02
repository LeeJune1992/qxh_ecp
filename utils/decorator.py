#coding=utf-8
import time
from utils.memcached import cache
from functools import wraps
from flask.ext.login import current_user,login_required
from flask import current_app,abort,request,jsonify
from flask import session
import logging
#from flask.ext.principal import Permission,ActionNeed

THREAD_CACHES = {}
def cached(cache_key='',thread_cache=False,timeout_seconds=0):
    def _cached(func):
        def do_cache(*args, **kws):
            if isinstance(cache_key,str):key=cache_key
            elif callable(cache_key):key = cache_key(*args,**kws)
            if thread_cache is True:
                if THREAD_CACHES.has_key(cache_key):
                    return THREAD_CACHES[cache_key]
            data = cache.get(key)
            if data is not None:return data
            data = func(*args, **kws)
            cache.set(key,data,timeout_seconds)
            if thread_cache is True:THREAD_CACHES[key] = data
            return data
        return do_cache
    return _cached


class view_cached_cls(object):
    def __init__(self, timeout=None):
        self.timeout = timeout or 3600*24

    def __call__(self, f):
        def decorator(*args, **kwargs):
            response = cache.get(request.path)
            if response is None:
                response = f(*args, **kwargs)
                cache.set(request.path, response, self.timeout)
            return response
        return decorator

view_cached = view_cached_cls()

def admin_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        slog = request.method,current_user.id,current_user.nickname,time.strftime("%Y-%m-%d %X", time.localtime()),request,request.form
        logging.error(slog)
        print slog
        clog = cache.get('johnlog')
        if not clog:
            print '99999999999999'
            cache.set('johnlog',slog)
        
        slog = cache.get('johnlog')
        print slog
        
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        if current_user.action(fn.__name__):
            return fn(*args, **kwargs)
        if request.is_xhr:return jsonify(result=False,error=u'权限不1足')
        abort(403)
    return decorated_view

