import {map} from 'd3-collection';
import {decodeJWToken, LuxException} from '../core/utils';
import {urlIsSameOrigin, urlResolve, urlIsAbsolute, urlJoin} from '../core/urls';
import paginator from './paginator';
import _ from '../ng';


const ENCODE_URL_METHODS = ['delete', 'get', 'head', 'options'];
//  HTTP verbs which don't send a csrf token in their requests
const NO_CSRF = ['get', 'head', 'options'];
//
let luxId = 0;


// @ngInject
export default function ($location, $window, $http, $log, $timeout, luxMessage, luxLazy) {

    var doc = $window.document,
        context = $window.lux,
        name = _.element(doc.querySelector('meta[name=csrf-param]')).attr('content'),
        token = _.element(doc.querySelector('meta[name=csrf-token]')).attr('content'),
        user = _.element(doc.querySelector('meta[name=user-token]')).attr('content');

    if (_.isString(context)) context = decodeJWToken(context);
    if (!_.isObject(context)) context = {};

    if (name && token) {
        context.csrf = {};
        context.csrf[name] = token;
    }
    if (user) {
        context.userToken = user;
        context.user = decodeJWToken(user)
    }

    return new Lux($window, $location, $http, $log, $timeout, context, luxMessage, luxLazy);
}


class Lux {

    constructor ($window, $location, $http, $log, $timeout, context, luxMessage, luxLazy) {
        this.$window = $window;
        this.$location = $location;
        this.$http = $http;
        this.$log = $log;
        this.$timeout = $timeout;
        this.$apis = map();
        this.messages = luxMessage;
        this.lazy = luxLazy;
        this.context = context;
    }

    // Return the csrf key-value token to post in forms
    get csrf () {
        return this.context.csrf;
    }

    get user () {
        return this.context.user;
    }

    get userToken () {
        return this.context.userToken;
    }

    api (action, ApiClass) {
        if (arguments.length === 2) {
            if (!_.isString(action)) throw new LuxException(action, 'action must be a string');
            this.$apis.set(action, ApiClass);
            return ApiClass;
        }

        if (_.isString(action)) action = {url: action};
        else action = _.extend({}, action);

        if (!_.isString(action.url))
            throw new LuxException(action, 'action must be an object with url property');

        var url = action.url,
            path = url,
            local = true;
        if (urlIsAbsolute(url)) {
            url = urlResolve(url);
            local = urlIsSameOrigin(url);
            path = url.pathname;
        }

        if (local) {
            action.baseUrl = '';
            ApiClass = this.$apis.get(action.baseUrl);
            if (!ApiClass) ApiClass = this.api('', WebApi);
        } else {
            action.baseUrl = url.$base();
            ApiClass = this.$apis.get(action.baseUrl);
            if (!ApiClass) ApiClass = this.api(action.baseUrl, RestApi);
        }

        action.path = urlJoin(path, action.path);

        return new ApiClass(this, action);
    }

    id (prefix) {
        return (prefix || 'l') + (++luxId);
    }

    logout (e, url) {
        e.preventDefault();
        var api = this.api(url),
            self = this;

        api.post().then(function () {
            if (self.context.POST_LOGOUT_URL) {
                self.$window.location.href = self.context.POST_LOGOUT_URL;
            } else {
                self.$window.location.reload();
            }
        }, function () {
            self.messages.error('Error while logging out');
        });
    }
}


class Api {

    constructor (lux, defaults) {
        this.$lux = lux;
        this.$defaults = defaults;
    }

    get baseUrl () {
        return this.$defaults.baseUrl;
    }

    get url () {
        return urlJoin(this.$defaults.baseUrl, this.$defaults.path);
    }

    get params () {
        return this.$defaults.params || {};
    }

    get path () {
        return this.$defaults.path;
    }

    get (opts) {
        return this.request('get', opts);
    }

    post (opts) {
        return this.request('post', opts);
    }

    put (opts) {
        return this.request('put', opts);
    }

    head (opts) {
        return this.request('head', opts);
    }

    delete (opts) {
        return this.request('delete', opts);
    }

    paginator () {
        return new paginator(this);
    }

    httpOptions () {}

    request (method, opts) {
        if (!opts) opts = {};
        // handle urlparams when not an object
        var $lux = this.$lux,
            options = {
                method: method.toLowerCase(),
                params: _.extend({}, this.params, opts.params),
                headers: opts.headers || {},
                url: urlJoin(this.url, opts.path)
            };

        if (ENCODE_URL_METHODS.indexOf(options.method) === -1) options.data = opts.data;

        if (!options.headers.hasOwnProperty('Content-Type'))
            options.headers['Content-Type'] = 'application/json';

        this.httpOptions(options);
        //
        return $lux.$http(options);
    }

}


class WebApi extends Api {

    httpOptions (options) {
        var $lux = this.$lux;

        if ($lux.csrf && NO_CSRF.indexOf(options.method === -1))
            options.data = _.extend(options.data || {}, $lux.csrf);
    }

}


class RestApi extends Api {

    httpOptions (options) {
        var $lux = this.$lux;

        var token = $lux.userToken;

        if (token)
            options.headers.Authorization = 'Bearer ' + token;
    }
}
