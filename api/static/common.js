function makeUrl(api, ws) {
    let scheme = window.location.protocol;
    let url = scheme + '//' + window.location.host + '/interactive_api/' + api;
    if(ws == 'ws' && scheme == 'https:'){
        url = 'wss' + '://' + window.location.host + '/interactive_api/' + api;
    }else if(ws == 'ws'){
        url = 'ws' + '://' + window.location.host + '/interactive_api/' + api;
    }
    return url;
}

function postJSON(url, data){
    return $.ajax({url:makeUrl(url),data:JSON.stringify(data),type:'POST', contentType:'application/json'});
}

function postFile(url, data){
    return $.ajax({url:makeUrl(url),data:data,type:'POST', processData:false, contentType:false});
}

function getJSON(url, data){
    return $.ajax({url:makeUrl(url),data:JSON.stringify(data),type:'GET', contentType:'application/json'});
}

function connectWS() {
    window.wsOpen = false;
    if ("WebSocket" in window){
        // 打开一个 web socket
        window.ws = new WebSocket(makeUrl('activity_live/', 'ws'));
        ws.onopen = function(){
            window.wsOpen = true;
            sendMessage();
        };
        ws.onmessage = function (evt){
            var received_msg = evt.data;
        };
        ws.onclose = function(){
            // 关闭 websocket
            window.wsOpen = false;
        };
    }else{
        // 浏览器不支持 WebSocket
        alert("您的浏览器不支持 WebSocket!");
    }
}

function sendMessage() {
    if(window.wsOpen != undefined && window.wsOpen == true && window.socketMsgQueue != undefined){
        $(window.socketMsgQueue).each(function(){
            window.ws.send(JSON.stringify($(this)[0]));
        });
    }
}

function makePostData(obj) {
    let data = {}
    $("input[type=text], select", obj).each(function(){
        data[$(this).attr('name')] = $(this).val()
    });
    $("input[type=checkbox]", obj).each(function(){
        data[$(this).attr('name')] = $(this).is(':checked')?true:false;
    });
    return data;
}

function scrollBar(obj) {
    obj.scrollTop(10);
    return $("body").scrollTop()>0;
    obj.scrollTop(0);
}
