angular.module('lux.cms.component', ['lux.services'])
    //
    // Defaults for cms components
    .value('cmsDefaults', {
    })
    //
    .factory('Component', ['$q', '$rootScope', function($q, $rootScope) {
        /**
         * Component provides the ability to register public methods events inside an app and allow
         * for other components to use the component via featureName.raise.methodName and featureName.on.eventName(function(args){}).
         *
         * @appInstance: App which the API is for
         * @compnentId: Unique id in case multiple API instances do exist inside the same Angular environment
         */
        var Component = function Component(appInstance, componentId) {
            this.gantt = appInstance;
            this.componentId = componentId;
            this.eventListeners = [];
        };

        /**
         * Registers a new event for the given feature.
         *
         * @featureName: Name of the feature that raises the event
         * @eventName: Name of the event
         *
         * To trigger the event call:
         * .raise.eventName()
         *
         * To register a event listener call:
         * .on.eventName(scope, callBackFn, _this)
         * scope: A scope reference to add a deregister call to the scopes .$on('destroy')
         * callBackFn: The function to call
         * _this: Optional this context variable for callbackFn. If omitted, gantt.api will be used for the context
         *
         * .on.eventName returns a de-register funtion that will remove the listener. It's not necessary to use it as the listener
         * will be removed when the scope is destroyed.
         */
        Component.prototype.registerEvent = function(featureName, eventName) {
            var self = this;
            if (!self[featureName]) {
                self[featureName] = {};
            }

            var feature = self[featureName];
            if (!feature.on) {
                feature.on = {};
                feature.raise = {};
            }

            var eventId = 'event:component:' + this.componentId + ':' + featureName + ':' + eventName;

            // Creating raise event method: featureName.raise.eventName
            feature.raise[eventName] = function() {
                $rootScope.$emit.apply($rootScope, [eventId].concat(Array.prototype.slice.call(arguments)));
            };

            // Creating on event method: featureName.oneventName
            feature.on[eventName] = function(scope, handler, _this) {
                var deregAngularOn = registerEventWithAngular(eventId, handler, self.gantt, _this);

                var listener = {
                    handler: handler,
                    dereg: deregAngularOn,
                    eventId: eventId,
                    scope: scope,
                    _this: _this
                };
                self.eventListeners.push(listener);

                var removeListener = function() {
                    listener.dereg();
                    var index = self.eventListeners.indexOf(listener);
                    self.eventListeners.splice(index, 1);
                };

                scope.$on('$destroy', function() {
                    removeListener();
                });

                return removeListener;
            };
        };

        /**
         * @ngdoc function
         * @name registerEventsFromObject
         * @description Registers features and events from a simple objectMap.
         * eventObjectMap must be in this format (multiple features allowed)
         * <pre>
         * {featureName:
         *        {
         *          eventNameOne:function(args){},
         *          eventNameTwo:function(args){}
         *        }
         *  }
         * </pre>
         * @param {object} eventObjectMap map of feature/event names
         */
        Component.prototype.registerEventsFromObject = function (eventObjectMap) {
          var self = this;
          var features = [];
          angular.forEach(eventObjectMap, function (featProp, featPropName) {
            var feature = {name: featPropName, events: []};
            angular.forEach(featProp, function (prop, propName) {
              feature.events.push(propName);
            });
            features.push(feature);
          });

          features.forEach(function (feature) {
            feature.events.forEach(function (event) {
              self.registerEvent(feature.name, event);
            });
          });

        };


        function registerEventWithAngular(eventId, handler, app, _this) {
            return $rootScope.$on(eventId, function() {
                var args = Array.prototype.slice.call(arguments);
                args.splice(0, 1); // Remove evt argument
                handler.apply(_this ? _this : app, args);
            });
        }

        /**
         * Registers a new event for the given feature
         *
         * @featureName: Name of the feature
         * @methodName: Name of the method
         * @callBackFn: Function to execute
         * @_this: Binds callBackFn 'this' to _this. Defaults to Api.app
         */
        Component.prototype.registerMethod = function(featureName, methodName, callBackFn, _this) {
            var self = this;

            if (!this[featureName]) {
                this[featureName] = {};
            }

            var feature = this[featureName];
            feature[methodName] = function() {
                callBackFn.apply(_this || this.app, arguments);
            };
        };

        /**
         * @ngdoc function
         * @name registerMethodsFromObject
         * @description Registers features and methods from a simple objectMap.
         * eventObjectMap must be in this format (multiple features allowed)
         * <br>
         * {featureName:
         *        {
         *          methodNameOne:function(args){},
         *          methodNameTwo:function(args){}
         *        }
         * @param {object} eventObjectMap map of feature/event names
         * @param {object} _this binds this to _this for all functions.  Defaults to gridApi.grid
         */
        Component.prototype.registerMethodsFromObject = function (methodMap, _this) {
          var self = this;
          var features = [];
          angular.forEach(methodMap, function (featProp, featPropName) {
            var feature = {name: featPropName, methods: []};
            angular.forEach(featProp, function (prop, propName) {
              feature.methods.push({name: propName, fn: prop});
            });
            features.push(feature);
          });

          features.forEach(function (feature) {
            feature.methods.forEach(function (method) {
              self.registerMethod(feature.name, method.name, method.fn, _this);
            });
          });

        };

        return Component;
    }]);
