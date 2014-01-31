//	bitcoin project
var body = $('body'),
    url = body.data('bitcoinurl'),
    sock = new WebSocket(url);
sock.onopen = function() {
    console.log('open');
};
sock.onmessage = function(e) {
    console.log('message', e.data);
};
sock.onclose = function() {
    console.log('close');
};
