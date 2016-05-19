import {default as _} from '../ng';


export default function () {

    const formMap = {},
        wrapperMap = {},    // container of Html wrappers for form elements
        actionMap = {},     // container of actions on a form
        successHooks = {},  // collection of handlers invoked on successful submit
        errors = {},
        tagMap = {
            date: 'input',
            datetime: 'input',
            email: 'input',
            hidden: 'input',
            month: 'input',
            number: 'input',
            password: 'input',
            search: 'input',
            tel: 'input',
            text: 'input',
            time: 'input',
            url: 'input',
            week: 'input'
        };

    let formCount = 1;

    _.extend(this, {
        setType,
        getType,
        setWrapper,
        getWrapper,
        getTag: getTag,
        setTag: setTag,
        getAction: getAction,
        setAction: setAction,
        onSuccess: onSuccess,
        error: error,
        id: formid,
        // Required for angular providers
        $get: () => this
    });

    function formid () {
        return 'lf' + (++formCount);
    }

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
        name = getTag(name);
        return form[name];
    }

    function setWrapper (wrapper) {
        if (_.isObject(wrapper) && _.isString(wrapper.name) && _.isFunction(wrapper.template)) {
            wrapperMap[wrapper.name] = wrapper;
        }
    }

    function getWrapper (name) {
        return wrapperMap[name];
    }

    function setTag (type, tag) {
        tagMap[type] = tag;
    }

    function getTag (type) {
        return tagMap[type] || type;
    }

    function getAction (type) {
        return actionMap[type];
    }

    function setAction (type, action) {
        actionMap[type] = action;
    }

    function onSuccess (type, hook) {
        if (arguments.length === 2) {
            successHooks[type] = hook;
            return this;
        } else
            return successHooks[type] || successHooks['default'];
    }

    function error (name, message) {
        if (arguments.length === 2) {
            errors[name] = message;
            return this;
        } else {
            var obj = name.$error,
                errorHandler;
            for (let key in obj) {
                if (obj.hasOwnProperty(key) && obj[key]) {
                    errorHandler = errors[key];
                    if (errorHandler)
                        break;
                }
            }

            if (_.isFunction(errorHandler))
                return errorHandler(name);
            else
                return errorHandler;

        }
    }
}
