import os, json
from form import ractive, Form
from osutils import get_files

@ractive
def index():
    return dict()

@ractive
def files():
    files = get_files(path=request.folder)
    alerts = []
    user = {'first_name':'Massimo'}
    form = request.forms.get('0')
    if form:        
        # save file
        filename = os.path.abspath(os.path.join(request.folder,form['filename']))
        if filename.startswith(request.folder):
            bytes = form.get('bytes')
            if bytes is not None:
                open(filename,'w').write(bytes)
    # open file
    bytes = None
    filename = None
    if request.vars.filename:
        filename = os.path.join(request.folder,request.vars.filename)
        if os.path.exists(filename):
            if os.path.getsize(filename)<1e6:
                bytes = open(filename).read()
                filename = filename[len(request.folder):]
                try:
                    json.dumps(bytes)
                except:
                    bytes = None
                    alerts.append({'info':'File is not a text file'})
            else:
                alerts.append({'info':'File is too large'})
        else:
            alerts.append({'error':'File does not exist'})
    return dict(menu = files, user=user, alerts=alerts, forms=[dict(bytes=bytes,filename=filename)])

@ractive
def form():
    """
    form = [
        {'name':'_formname','type':'hidden','value':''},
        {'name':'_csrfkey','type':'hidden','value':''},
        {'name':'first_name','type':'string','label':'First Name','value':''},
        {'name':'last_name','type':'string','label':'Last Name','value':''},
        {'name':'date','type':'date','label':'Date','value':''},
        {'name':'time','type':'time','label':'Time','value':''},
        {'name':'datetime','type':'datetime','label':'DateTime','value':''},
        {'name':'integer','type':'integer','label':'Integer','value':''},
        {'name':'double','type':'double','label':'Double','value':''},
        {'type':'submit','value':'submit'},
        ]
    """
    alerts = []
    form = Form(db.thing).process(request.forms.get('0'))
    if form.errors: alerts.append({'error':'Invalid form'})
    table = db(db.thing).select().xml() # this should move to JS too
    return dict(forms = [form], table=table, alerts=alerts)

@ractive
def markmin():
    bytes = open(os.path.join(request.folder,'private','example.mm2')).read()
    return dict(forms = [{'filename':'example','bytes':bytes}])
