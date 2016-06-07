import _ from '../ng';
import reverseMerge from '../core/reversemerge';


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


export function mergeOptions(field, defaults, $scope) {
    var cfg = field.$cfg;
    if (_.isFunction(defaults)) defaults = defaults(field, $scope);
    reverseMerge(field, defaults);
    if (field.$luxform && field.$luxform !== field)
        _.forEach(cfg.inheritAttributes, (attr) => {
            if (_.isUndefined(field[attr]))
                field[attr] = field.$luxform[attr];
        });
    if (field.type === 'hidden')
        field.labelSrOnly = true;
}

// sort-of stateless util functions
export function asHtml(el) {
    const wrapper = _.element('<a></a>');
    return wrapper.append(el).html();
}


export function compile(lazy, html, scope, cloneAttachFunc) {
    lazy.$compile(html)(scope, cloneAttachFunc);
}


export function mergeArray (array1, array2) {
    if (_.isArray(array1) && _.isArray(array2))
        array2.forEach((value, index) => {
            array1[index] = value;
        });
    return array1;
}
