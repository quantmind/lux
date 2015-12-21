// Lux pagination module for controlling the flow of
// repeat requests to the API.
// It can return all data at an end point or offer
// the next page on request for the relevant component

angular.module('lux.pagination', ['lux.services'])

    .factory('LuxPagination', ['$lux', function($lux) {

        // LuxPagination constructor requires three args
        // @param scope - the angular $scope of component's directive
        // @param target - object containing name and url, e.g.
        // {name: "groups_url", url: "http://127.0.0.1:6050"}
        // @param recursive - set to true if you want to recursively
        // request all data from the endpoint

        function LuxPagination(scope, target, recursive) {
            this.scope = scope;
            this.target = target;
            this.api = $lux.api(this.target);

            if (recursive === true) this.recursive = true;
        }

        LuxPagination.prototype.getData = function(params, cb) {
            // getData runs $lux.api.get() followed by the component's
            // callback on the returned data or error.
            // it's up to the component to handle the error.

            this.params = params ? params : null;
            if (cb) this.cb = cb;

            this.api.get(null, params).then(function(data) {

                this.cb(data);
                this.updateTarget(data);

            }.bind(this), function(error) {
                var err = {error: error};
                cb(err);
            });

        };

        LuxPagination.prototype.updateTarget = function(data) {
            // updateTarget creates an object containing the most
            // recent last and next links from the API

            if (data.data.last) {
                this.emitEvent();
                this.urls = {
                    last: data.data.last,
                    next: data.data.next ? data.data.next : false
                };
                if (this.recursive) this.loadMore();
            }

        };

        LuxPagination.prototype.emitEvent = function() {
            // emit event if more data available, the component can
            // listen for it and choose how to deal with it
            this.scope.$emit('moreData');
        };

        LuxPagination.prototype.loadMore = function() {
            // loadMore applies new urls from updateTarget to the
            // target object and makes another getData request.

            if (this.urls.next === false) {
                this.target.url = this.urls.last;
            } else if (this.urls.next) {
                this.target.url = this.urls.next;
            }

            // Call API with updated target URL
            this.getData();

        };

        return LuxPagination;

    }]);
