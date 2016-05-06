import {default as _} from '../ng';


export default function () {

    const formMap = {};

    _.extend(this, {
        setType,
        getType,
        // Required for angular providers
        $get: () => this
    });

    function setType (options) {
        if (_.isObject(options) && _.isString(options.name)) {
            var formName = options.form || 'default',
                form = formMap[formName];

            if (!form)
                formMap[formName] = form = {};

            if (formName !== 'default')
                options = _.extend({}, formMap.default[options.name], options);

            form[options.name] = options;
            return options;
        } else {
            throw Error(
                `An object with attribute name is required.
                Given: ${JSON.stringify(arguments)}
                `
            );
        }
    }

    function getType (name, formName) {
        formName = formName || 'default';
        var form = formMap[formName];
        if (!form) throw Error(`Form ${formName} is not available`);
        return form[name];
    }
}
