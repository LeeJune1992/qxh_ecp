#coding=utf-8
from werkzeug.contrib.cache import MemcachedCache
from global_settings import MEMCACHED_SERVER
cache = MemcachedCache(servers=MEMCACHED_SERVER,default_timeout=3600*24)