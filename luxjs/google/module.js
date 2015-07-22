    //
    //  Module for interacting with google API and services
    angular.module('lux.google', ['lux.services'])
        //
        .run(['$rootScope', '$lux', '$log', function (scope, $lux, log) {
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
            $lux.api('googlesheets', googlesheets);
        }])
        //
        .directive('googleMap', ['$lux', function ($lux) {
            return {
                //
                // Create via element tag
                // <d3-force data-width=300 data-height=200></d3-force>
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    if(!scope.googlemaps) {
                        $lux.log.error('Google maps url not available. Cannot load google maps directive');
                        return;
                    }
                    require([scope.googlemaps], function () {
                        var config = lux.getObject(attrs, 'config', scope),
                            lat = +config.lat,
                            lng = +config.lng,
                            loc = new google.maps.LatLng(lat, lng),
                            opts = {
                                center: loc,
                                zoom: config.zoom ? +config.zoom : 8,
                                mapTypeId: google.maps.MapTypeId.ROADMAP,
                                scrollwheel: config.scrollwheel ? true : false,
                            },
                            map = new google.maps.Map(element[0], opts),
                            //
                            marker = config.marker;

                        if (marker)
                            var gmarker = new google.maps.Marker(angular.extend({
                                position: loc,
                                map: map,
                            }, marker));
                        //
                        windowResize(function () {
                            google.maps.event.trigger(map, 'resize');
                            map.setCenter(loc);
                            map.setZoom(map.getZoom());
                        }, 500);
                    });
                }
            };
        }]);
