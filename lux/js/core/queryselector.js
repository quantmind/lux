import _ from '../ng';


export default function (elem, query) {
    if (arguments.length === 1 && _.isString(elem)) {
        query = elem;
        elem = document;
    }
    elem = _.element(elem);
    if (elem.length && query)
        return _.element(elem[0].querySelector(query));
    else
        return elem;
}
