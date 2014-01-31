//      luxweb - v0.1.0

//      Compiled 2014-01-31.
//      Copyright (c) 2014 - your name
//      Licensed .
//      For all details and documentation:
//      

define(['jquery', 'sockjs'], function ($) {
    "use strict";

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

//
});
