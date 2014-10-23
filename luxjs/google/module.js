    //
    //  Module for interacting with google API and services
    angular.module('lux.google', ['lux.api'])
        //
        .run(['$rootScope', '$lux', '$log', '$location', function (scope, $lux, log, location) {
            var analytics = scope.google ? scope.google.analytics : null;

            if (analytics && analytics.id) {
                var ga = analytics.ga || 'ga';
                if (typeof ga === 'string')
                    ga = root[ga];
                log.info('Register events for google analytics ' + analytics.id);
                scope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
                    var state = scope.$state;
                    //
                    if (state) {
                        var fromHref = stateHref(state, fromState, fromParams),
                            toHref = stateHref(state, toState, toParams);
                        if (fromHref !== 'null') {
                            if (fromHref !== toHref)
                                ga('send', 'pageview', {page: toHref});
                            else
                                ga('send', 'event', 'stateChange', toHref);
                            ga('send', 'event', 'fromState', fromHref, toHref);
                        }
                    }
                });
            }

            // Googlesheet api
            $lux.registerApi('googlesheets', {
                //
                endpoint: "https://spreadsheets.google.com",
                //
                url: function (urlparams) {
                    // when given the url is of the form key/worksheet where
                    // key is the key of the spreadsheet you want to retrieve,
                    // worksheet is the positional or unique identifier of the worksheet
                    if (this._url) {
                        if (urlparams) {
                            return this.endpoint + '/feeds/list/' + this._url + '/' + urlparams.id + '/public/values?alt=json';
                        } else {
                            return null;
                        }
                    }
                },
                //
                getList: function (options) {
                    var Model = this.Model,
                        opts = this.options,
                        $lux = this.$lux;
                    return this.request('GET', null, options).then(function (response) {
                        return response;
                    });
                },
                //
                get: function (urlparams, options) {
                    var Model = this.Model,
                        opts = this.options,
                        $lux = this.$lux;
                    return this.request('GET', urlparams, options).then(function (response) {
                        response.data = opts.orientation === 'columns' ? new GoogleSeries(
                            $lux, response.data) : new GoogleModel($lux, response.data);
                        return response;
                    });
                }
            });

        }])
        //
        .directive('googleMap', function () {
            return {
                //
                // Create via element tag
                // <d3-force data-width=300 data-height=200></d3-force>
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    require(['google-maps'], function () {
                        on_google_map_loaded(function () {
                            var lat = +attrs.lat,
                                lng = +attrs.lng,
                                loc = new google.maps.LatLng(lat, lng),
                                opts = {
                                    center: loc,
                                    zoom: attrs.zoom ? +attrs.zoom : 8
                                },
                                map = new google.maps.Map(element[0], opts);
                            var marker = new google.maps.Marker({
                                position: loc,
                                map: map,
                                title: attrs.marker
                            });
                            //
                            windowResize(function () {
                                google.maps.event.trigger(map, 'resize');
                                map.setCenter(loc);
                                map.setZoom(map.getZoom());
                            }, 500);
                        });
                    });
                }
            };
        });