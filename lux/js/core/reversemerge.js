import _ from '../ng';

export default function (target, defaults) {
    if (!_.isObject(target)) return;

    _.forEach(defaults, (value, key) => {
        if (!target.hasOwnProperty(key)) target[key] = value;
    });

    return target;
}
