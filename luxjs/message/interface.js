
    lux.messageService = {
        pushMessage: function () {},

        debug: function (text) {
            this.pushMessage({type: 'debug', text: text});
        },

        info: function (text) {
            this.pushMessage({type: 'info', text: text});
        },

        success: function (text) {
            this.pushMessage({type: 'success', text: text});
        },

        warn: function (text) {
            this.pushMessage({type: 'warn', text: text});
        },

        error: function (text) {
            this.pushMessage({type: 'error', text: text});
        },

        log: function ($log, message) {
            var type = message.type;
            if (type === 'success') type = 'info';
            $log[type](message.text);
        }
    };
