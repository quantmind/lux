
// @ngInject
export default function ($rootScope, $log) {

    return new MessageService($rootScope, $log);

}


class MessageService {

    constructor ($scope, $log) {
        this.$scope = $scope;
        this.$log = $log;
    }

    log (level, message, opts) {
        var $log = this.$log;
        if (!$log[level]) level = 'info';
        $log[level](message);
        if (opts && opts.broadcast === false) return;
        if (!opts) opts = {}
        opts.text = message;
        opts.level = level;
        this.$scope.$broadcast('messageAdded', opts);
    }

    debug (text, opts) {
        if (arguments.length === 1) opts = {broadcast: false};
        this.log('debug', text, opts);
    }

    info (text, opts) {
        this.log('info', text, opts);
    }

    success (text, opts) {
        this.log('success', text, opts);
    }

    warn (text, opts) {
        this.log('warn', text, opts);
    }

    error (text, opts) {
        this.log('error', text, opts);
    }

    clear (id) {
        this.$scope.$broadcast('messageRemove', id);
    }
}
