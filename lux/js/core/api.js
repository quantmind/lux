import {map} from 'd3-collection';
import {decodeJWToken} from './utils';
import _ from '../ng';


// @ngInject
export default function ($location, $window, $q, $http, $log, $timeout) {

    var doc = $window.document,
        context = $window.lux,
        name = _.element(doc.querySelector('meta[name=csrf-param]')).attr('content'),
        token = _.element(doc.querySelector('meta[name=csrf-token]')).attr('content'),
        user = _.element(doc.querySelector('meta[name=user-token]')).attr('content');

    if (!_.isObject(context)) context = {};

    if (name && token) {
        context.csrf = {};
        context.csrf[name] = token;
    }
    if (user) {
        context.userToken = user;
        context.user = decodeJWToken(user)
    }

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

    // Return the csrf key-value token to post in forms
    get csrf () {
        return this.context.csrf;
    }

    get userToken () {
        return this.context.userToken;
    }
}
