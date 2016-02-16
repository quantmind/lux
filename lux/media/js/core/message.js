define(['lux/config/main'], function (lux) {
    'use strict';

    function asMessage(level, message) {
        if (lux.isString(message)) message = {text: message};
        message.type = level;
        return message;
    }

    lux.messageService = {
        pushMessage: function () {
        },

        debug: function (text) {
            this.pushMessage(asMessage('debug', text));
        },

        info: function (text) {
            this.pushMessage(asMessage('info', text));
        },

        success: function (text) {
            this.pushMessage(asMessage('success', text));
        },

        warn: function (text) {
            this.pushMessage(asMessage('warn', text));
        },

        error: function (text) {
            this.pushMessage(asMessage('error', text));
        },

        log: function ($log, message) {
            var type = message.type;
            if (type === 'success') type = 'info';
            $log[type](message.text);
        }
    };

    lux.messages = lux.extend(lux.messages);

    return lux.messageService;
});
