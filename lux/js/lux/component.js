import _ from '../ng';


export default class LuxComponent {

    constructor ($lux) {
        this.$lux = $lux;
        this.$id = $lux.id();
    }

    get $log () {
        return this.$lux.$log;
    }

    get $compile () {
        return this.$lux.$compile;
    }

    get $injector () {
        return this.$lux.$injector;
    }

    get $window () {
        return this.$lux.$window;
    }

    get $timeout () {
        return this.$lux.$timeout;
    }

    addMessages (messages, level) {
        if (!level) level = 'info';
        var $lux = this.$lux,
            opts = {rel: this.$id};

        if (!_.isArray(messages)) messages = [messages];
        _.forEach(messages, (message) => {
            $lux.messages.log(level, message, opts);
        });
    }
}
