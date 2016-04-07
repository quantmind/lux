// Lux pagination module for controlling the flow of
// repeat requests to the API.
// It can return all data at an end point or offer
// the next page on request for the relevant component
define(['angular',
        'lux/services/main'], function (angular) {
    'use strict';

    angular.module('lux.services.pagination', ['lux.services'])

        .factory('luxPagination', ['$lux', function ($lux) {


            function luxPagination (scope, target, recursive) {
                return new LuxPagination($lux, scope, target, recursive);
            }

            luxPagination.prototype = LuxPagination.prototype;

            return luxPagination;

        }]);


    /**
    * LuxPagination constructor requires three args
    * @param scope - the angular $scope of component's directive
    * @param target {object} - containing name and url, e.g.
    * {name: "groups_url", url: "http://127.0.0.1:6050"}
    * @param recursive {boolean}- set to true if you want to recursively
    * request all data from the endpoint
    */
    function LuxPagination($lux, scope, target, recursive) {
        this.scope = scope;
        this.target = target;
        this.orgUrl = this.target.url;
        this.$lux = $lux;
        this.api = $lux.api(this.target);
        this.recursive = recursive === true ? true : false;
    }


    LuxPagination.prototype.getData = function(params, cb) {
        // getData runs $lux.api.get() followed by the component's
        // callback on the returned data or error.
        // it's up to the component to handle the error.

        this.params = params ? params : null;
        if (cb) this.cb = cb;

        this.api.get(null, this.params).then(function(data) {

            // removes search from parameters so this.params is
            // clean for next generic loadMore or new search. Also
            // adds searched flag.
            if (this.searchField) {
                data.searched = true;
                delete this.params[this.searchField];
            }

            this.cb(data);
            this.updateUrls(data);

        }.bind(this), function(error) {
            this.cb(error);
        }.bind(this));

    };

    LuxPagination.prototype.updateUrls = function(data) {
        // updateUrls creates an object containing the most
        // recent last and next links from the API

        if (data && data.data && data.data.last) {
            this.urls = {
                last: data.data.last,
                next: data.data.next ? data.data.next : false
            };
            // If the recursive param was set to true this will
            // request data using the 'next' link; if not it will emitEvent
            // so the component knows there's more data available
            if (this.recursive) this.loadMore();
            else this.emitEvent();
        }

    };

    LuxPagination.prototype.emitEvent = function() {
        // emit event if more data available, the component can
        // listen for it and choose how to deal with it
        this.scope.$emit('moreData');
    };

    LuxPagination.prototype.loadMore = function() {
        // loadMore applies new urls from updateUrls to the
        // target object and makes another getData request.

        if (!this.urls.next && !this.urls.last) throw 'Updated URLs not set.';

        if (this.urls.next === false) {
            this.target.url = this.urls.last;
        } else if (this.urls.next) {
            this.target.url = this.urls.next;
        }

        // Call API with updated target URL
        this.getData(this.params);

    };

    LuxPagination.prototype.search = function(query, searchField) {
        this.searchField = searchField;
        this.params = this.params || {};
        this.params[this.searchField] = query;
        // Set current target URL to the original target URL to reset any
        // existing limits/offsets so full endpoint is searched
        this.target.url = this.orgUrl;

        this.getData(this.params);
    };
});
