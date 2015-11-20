import json
from gluon.utils import web2py_uuid
from gluon import serializers, current, URL, current

def ractive(f):
    def tmp():
        request = current.request
        response = current.response
        response.delimiters = '{%','%}'
        request.forms = {}
        if request.env.request_method=='POST':
            try: data = json.load(request.body)
            except: pass
            else:
                if isinstance(data,dict) and 'forms' in data:
                    request.forms = data['forms']
        data = serializers.json(f())
        path = serializers.json('/'.join(URL().split('/')[:4])+'/')
        response.delimiters = ['{%','%}']
        if request.env.get('content_type','').split(';')[0] == 'application/json':
            response.headers['Content-Type'] = 'application/json'
            return data
        return dict(DATA=data,PATH=path)
    return tmp

class Form(object):    
    def __init__(self, table, record=None, deletable=False, csrf_protection=True):
        self.table = table
        self.record = record
        self.deletable = deletable
        self.csrf_protection = csrf_protection
        self.values = {}
        self.errors = {}
        self.processed = False
        self.accepted = False
        self.deleted = False
    def process(self, vars):
        self.errors.clear()
        self.values.clear()
        if vars and not self.processed:
            if self.csrf_protection:
                if vars and (vars[0].get('name')!='_csrf' or 
                             vars[0].get('value') != current.session._csrf):
                    return self        
            self.processed = True
            id = self.record.id if hasattr(self.record,'id') else self.record
            recordset = self.table._db(self.table.id==id)
            
            if [var for var in vars if var.get('name')=='_delete_record' and var.get('value')]:
                recordset.delete()
                self.deleted = True
                self.accepted = True
                return self

            fieldnames = self.table.fields
            for item in vars:
                name = item.get('name')
                if name and name in fieldnames and 'value' in item:
                    value = item['value']
                    if self.table[name].type=='upload':
                        keep = value.get('keep')
                        if keep:
                            continue
                        elif 'data' in value:
                            value['data'] = value['data'].encode('latin-1')
                        elif not keep:
                            value = None
                    (value,error) = self.table[name].validate(value)
                    if error:
                        self.errors[name] = error
                    self.values[item['name']] = value
            if not self.errors:
                self.accepted = True
                if not self.record:
                    self.table.insert(**self.values)            
                else:
                    if 'id' in self.values:
                        self.values.pop('id')
                    recordset.update(**self.values)
        return self
    def as_list(self):
        form = []
        if self.csrf_protection:
            current.session._csrf = current.session._csrf or web2py_uuid()
            form.append({'name':'_csrf','type':'hidden','value':current.session._csrf})
        if self.record:
            record = self.record if hasattr(self.record,'id') else self.table[self.record]
            if not record:
                return []
        for field in self.table:
            try:
                options = [{'value':o[0],'label':o[1]} for o in field.requires.options()]
            except:
                options = None
            if self.record and record and field.name in record:
                value = record[field.name]
            else:
                value = field.default
            row = {'name':field.name,
                   'type':field.type,
                   'label':field.label,
                   'options':options,
                   'error':self.errors.get(field.name,None)}
            if field.type == 'upload':
                row['value'] = {'link':value,'keep':True}
            else:
                row['value'] = self.values.get(field.name,value)            
            form.append(row)
        if self.deletable and self.record:
            row = {'name':'_delete_record',
                   'type':'boolean',
                   'label':'Delete?',
                   'value':False}
            form.append(row)
        form.append({'type':'submit','value':'submit'})        
        return form

