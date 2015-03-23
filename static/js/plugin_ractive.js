// /////////////////////
// Ractive decorators of tags, date, time, datetime widgets
// /////////////////////
Ractive.decorators.tagsinput = function (node) {
    var item = jQuery(node);
    item.tagsinput();
    var update = function(){ 
        // remove duplicates invisible (weird interaction of rative and plugin)
        item.find('option:not([selected])').remove();
        // remove all leading and training spaces
        item.find('option').each(function()
           {var t=jQuery(this); t.val(t.val().replace(/^\s+|\s+$/g,''));});
        // tell ractive the plugin has changed the data
        ractive.updateModel(); 
        
    };
    item.on('itemAdded',update).on('itemRemoved',update);
    return { teardown: function () {} };
};

Ractive.decorators.datetimeinput = function (node) {
    var item = jQuery(node);
    var format = item.data('format')||"%Y-%m-%d %H:%M:%S";
    Calendar.setup({ inputField: node, showsTime: true, timeFormat: "24", ifFormat: format});
    return { teardown: function () {} };
};

Ractive.decorators.dateinput = function (node) {
    var item = jQuery(node);
    var format = item.data('format')||"%Y-%m-%d";
    Calendar.setup({ inputField: node, showsTime: false, ifFormat: format});
    return { teardown: function () {} };
};

Ractive.decorators.timeinput = function (node) {
    var item = jQuery(node);
    item.timeEntry({ spinnerImage: ''});
    return { teardown: function () {} };
};

// ///////////////////////////////////
// create the ractive object
// ///////////////////////////////////
var ractive = new Ractive({ el: 'wrapper', 
                            template: '#ractive-main-template', 
                            data:RACTIVE_DATA });

// ///////////////////////////////////
// register useful events
// ///////////////////////////////////
ractive.on('save',function(event,form_name){
        event.original.preventDefault();
        var data = {'forms':{}};
        data.forms[form_name] = ractive.data.forms[form_name];
        var info = {url:window.location.href, method:'POST', contentType:'application/json',
                    data:JSON.stringify(data), processData:false};
        jQuery.ajax(info)
            .then(function(data){
                    if(data.redirect) window.location=data.redirect;
                    else {for(var key in data) 
                            ractive.set(key,data[key]); ractive.fire('saved',data);}
                }).fail(function(data){alert("Network error: "+data);});
    });

// ///////////////////////////////////
// define validators for forms
// ///////////////////////////////////
String.prototype.reverse = function() {
    return this.split('').reverse().join('');
};

ractive.on('validate-integer',function(event) {
        console.log(event.node.value);
        var nvalue = event.node.value.reverse()
            .replace(/[^0-9\-]|\-(?=.)/g, '').reverse();
        if(event.node.value != nvalue) event.node.value = nvalue;
    });

ractive.on('validate-double',function(event) {
        var nvalue = event.node.value.reverse()
            .replace(/[^0-9\-\.,]|[\-](?=.)|[\.,](?=[0-9]*[\.,\\])/g, '').reverse();
        if(event.node.value != nvalue) event.node.value = nvalue;
    });

ractive.on('magic-upload',function(event) {        
        var file = event.node.files[0];
        var reader = new FileReader();
        var form_name = event.node.getAttribute('data-form-name');
        var name = event.node.getAttribute('name');
        var filename = file.name;
        var form = ractive.data.forms[form_name];
        var fields = form.filter(function(field){return field.name==name});
        if(file) {
            if(file.size>32*1024*1024) {
                fields[0].error = 'File too large to upload';
                ractive.set('forms',ractive.data.forms);
            } else {
                reader.onload = function(e) {                    
                    var data = e.target.result;
                    fields[0].value = {filename:filename, data:data};
                    fields[0].error = null;
                    ractive.set('forms',ractive.data.forms);
                }
                reader.readAsBinaryString(event.node.files[0]);            
            }
        }
    });