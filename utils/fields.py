# -*- coding: utf-8 -*-
import simplejson
import zlib
import uuid
from sqlalchemy import types
from utils.tools import c_dict

class UUID(types.TypeDecorator):
    impl = types.String
    def get_col_spec(self):
        return "uuid"

    def bind_processor(self, dialect):
        def process(value):
            return value
        return process

    def result_processor(self, dialect):
        def process(value):
            return value
        return process

class Dict(types.TypeDecorator):
    impl = types.String
    def process_bind_param(self, value, dialect):
        if not value:
            return None
        try:
            return ','.join('%s:%s'%(k,v,) for k,v in value.iteritems()) if isinstance(value,dict) else value
        except:
            raise ValueError('can\'t convert the dict(%s) to string value.'%str(value))

    def process_result_value(self, value, dialect):
        if isinstance(value,dict):
            return value
        try:
            return eval('{%s}'%value,c_dict) if value else {}
        except:
            raise ValueError('can\'t convert the string value(%s) to dict,please check DB data config.'%value)

class List(types.TypeDecorator):
    impl = types.String
    def process_bind_param(self, value, dialect):
        if not value:
            return None
        try:
            return ','.join(str(i) for i in value).replace('\'','').replace('"','') if isinstance(value,(list,tuple)) else value
        except:
            raise ValueError('can\'t convert the list(%s) to string value.'%str(value))

    def process_result_value(self, value, dialect):
        if isinstance(value,(list,tuple)):
            return value

        try:
            return eval('[%s]'%value,c_dict) if value else []
        except:
            print str(value)
            raise ValueError('can\'t convert the string value(%s) to list,please check DB data config.'%value)

class Json(types.TypeDecorator):
    impl = types.String
    def process_bind_param(self, value, dialect):
        try:
            return None if value is None else simplejson.dumps(value)
        except:
            return None

    def process_result_value(self, value, dialect):
        try:
            return None if value is None else simplejson.loads(value)
        except:
            return None

class Bson(types.TypeDecorator):
    impl = types.LargeBinary
    def process_bind_param(self, value, dialect):
        try:
            return None if value is None else zlib.compress(simplejson.dumps(value))
        except:
            raise ValueError('compress lib json data error.')

    def process_result_value(self, value, dialect):
        try:
            return None if value is None else simplejson.loads(zlib.decompress(value))
        except:
            raise ValueError('load lib json data error.')


class ChoiceType(types.TypeDecorator):
    impl = types.SmallInteger

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.iteritems() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]