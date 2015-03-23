db = DAL('sqlite://storage.sqlite')
from gluon.tools import Auth; auth = Auth(db); auth.define_tables();

db.define_table(
    'thing',
    Field('name',requires=IS_NOT_EMPTY()),
    Field('broken','boolean'),
    Field('age','integer'),
    Field('weight','double'),
    Field('created1_on','date'),
    Field('created2_on','time'),
    Field('created3_on','datetime'),
    Field('color',requires=IS_IN_SET(('red','green','blue'))),
    Field('tags','list:string',default=['pippo','pluto']),
    Field('info', 'text'),
    Field('filename','upload'))

