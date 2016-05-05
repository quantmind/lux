import {map} from 'd3-collection';
import {default as _} from '../angular-fix';


// @ngInject
export default function ($location, $window, $q, $http, $log, $timeout) {

    var doc = $window.document,
        context = $window.lux || {},
        name = _.element(doc.querySelector('meta[name=csrf-param]')).attr('content'),
        token = _.element(doc.querySelector('meta[name=csrf-token]')).attr('content'),
        user = _.element(doc.querySelector('meta[name=user-token]')).attr('content');

    if (name && token) {
        context.csrf = {};
        context.csrf[name] = token;
    }
    if (user) context.userToken = user;

    return new Lux($location, $q, $http, $log, $timeout, context);
}


class Lux {

    constructor ($location, $q, $http, $log, $timeout, context) {
        this.$location = $location;
        this.$q = $q;
        this.$http = $http;
        this.$log = $log;
        this.$timeout = $timeout;
        this.apis = map();
        this.context = context;
    }

    get csrf () {
        return this.context.csrf;
    }

    get userToken () {
        return this.context.userToken;
    }
}
