import {default as _} from '../ng';


export default function () {

    const formMap = {},
        wrapperMap = {},
        tagMap = {
            date: 'input',
            datetime: 'input',
            email: 'input',
            hidden: 'input',
            month: 'input',
            number: 'input',
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
}
