import json
from gluon import serializers, current, URL

def ractive(f):
    def tmp():
        request = current.request
        response = current.response
        if request.env.request_method=='POST':
            request.data = json.load(request.body)
        else:
            request.data = {}
        data = serializers.json(f())
        path = serializers.json('/'.join(URL().split('/')[:4])+'/')
        response.delimiters = ['{%','%}']
        if request.env.get('content_type','').split(';')[0] == 'application/json':
            response.headers['Content-Type'] = 'application/json'
            return data
        return dict(DATA=data,PATH=path)
    return tmp

class Form(object):    
    def __init__(self,table):
        self.table = table
        self.values = {}
        self.errors = {}
    def process(self, vars):
        self.errors.clear()
        self.values.clear()
        if vars:
            fieldnames = self.table.fields
            for item in vars:
                name = item.get('name')
                if name and name in fieldnames and 'value' in item:
                    (value,error) = self.table[name].validate(item['value'])
                    if error:
                        self.errors[name] = error
                    self.values[item['name']] = value
            if not self.errors:
                self.table.insert(**self.values)            
        return self
    def as_list(self):
        form = []
        for field in self.table:
            try:
                options = [{'value':o[0],'label':o[1]} for o in field.requires.options()]
            except:
                options = None
            form.append({'name':field.name,
                         'type':field.type,
                         'label':field.label,
                         'value':self.values.get(field.name,field.default),
                         'options':options,
                         'error':self.errors.get(field.name,None)})
        form.append({'type':'submit','value':'submit'})        
        return form
