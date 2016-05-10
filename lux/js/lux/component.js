import _ from '../ng';


export default class LuxComponent {

    constructor ($lux) {
        this.$lux = $lux;
        this.$id = $lux.id();
    }

    addMessages (messages, level) {
        if (!level) level = 'info';
        var $lux = this.$lux,
            opts = {rel: this.$id};

        if (_.isArray(messages)) messages = [messages];
        _.forEach(messages, (message) => {
            $lux.messages.log(level, message, opts);
        });
    }
}
