import os, re, collections, json
from form import ractive, Form

@ractive
def index():
    return dict(name=request.data.get('name','massimo'))

def get_files(path, ignore_dirs=['errors','sessions']):
    regex_folders = re.compile('^[\w].+[\w]$$')
    regex_files = re.compile('^[\w].+\.(py|html|css|js|jpe?g|png|gif|mpe?g4?)$')
    folder_maps = collections.defaultdict(list)
    folder_maps[path] = []
    for (root, dirnames, filenames) in os.walk(path, topdown=True):
        for dirname in dirnames:
            if regex_folders.match(dirname) and not dirname in ignore_dirs:
                children = []
                newpath = os.path.join(root,dirname) 
                folder_maps[newpath] = children
                folder_maps[root].append({'name':dirname,'children':children})
        for filename in filenames:
            if regex_files.match(filename):                
                link = URL(vars=dict(filename=os.path.join(root,filename)[len(path):]))
                folder_maps[root].append({'name':filename, 'link':link})
    files = folder_maps[path]
    return files

@ractive
def files():
    files = get_files(path=request.folder)
    alerts = []
    user = {'first_name':'Massimo'}
    if request.data:        
        filename = os.path.join(request.folder,request.data['filename'])
        bytes = request.data.get('bytes')
        if bytes is not None:
            open(filename,'w').write(bytes)
    bytes = None
    filename = None
    if request.vars.filename:
        filename = os.path.join(request.folder,request.vars.filename)
        if os.path.exists(filename):
            if os.path.getsize(filename)<1e6:
                bytes = open(filename).read()
                filename = filename[len(request.folder):]
                try: json.dumps(bytes)
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
    alerts = []
    form = Form(db.thing).process(request.data)
    if form.errors: alerts.append({'error':'Invalid form'})
    table = db(db.thing).select().xml() # this should move to JS too
    return dict(forms = [form], table=table, alerts=alerts)

@ractive
def markmin():
    bytes = open(os.path.join(request.folder,'private','example.mm2')).read()
    return dict(forms = [{'filename':'example','bytes':bytes}])
