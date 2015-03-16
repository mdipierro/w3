db = DAL('sqlite://storage.sqlite')

db.define_table(
    'thing',
    Field('name',requires=IS_NOT_EMPTY()),
    Field('broken','boolean'),
    Field('age','integer'),
    Field('color',requires=IS_IN_SET(('red','green','blue'))),
    Field('info', 'text'))

