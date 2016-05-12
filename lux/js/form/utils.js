import _ from '../ng';


export function defaultPlaceholder (field) {
    return field.label || field.title || field.name;
}


export function selectOptions (field) {
    var options = field.options;
    delete field.options;
    if (_.isString(options)) {
        // Assume a url
        field.$lux.api(options).get().then((response) => {
            if (response.status === 200)
                parseOptions(field, response.data);
        })
    } else {
        parseOptions(field, options);
    }

}


export function parseOptions (field, items, objParser) {
    if (!_.isArray(items)) items = [];
    field.options = items.map((opt) => {
        if (_.isArray(opt)) {
            opt = {
                value: opt[0],
                label: opt[1] || opt[0]
            }
        } else if (_.isObject(opt))
            opt = objParser ? objParser(opt) : opt;
        else
            opt = {value: opt, label: ''+opt};
        return opt;
    });
}
