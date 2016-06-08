import _ from '../ng';
import {Lux, windowContext} from './api';


// @ngInject
export default function ($controllerProvider, $provide, $compileProvider, $filterProvider,
                         $locationProvider, $injector) {

    var loading = false,
        loadingQueue = [],
        moduleCache = {},
        plugins = {},
        providers = {
            $controllerProvider: $controllerProvider,
            $compileProvider: $compileProvider,
            $filterProvider: $filterProvider,
            $locationProvider: $locationProvider,
            $provide: $provide, // other things (constant, decorator, provider, factory, service)
            $injector: $injector
        };

    $locationProvider.html5Mode({
        enabled: true,
        requireBase: false,
        rewriteLinks: false
    });

    _.extend(this, {
        // Required for angular providers
        plugins: plugins,
        $get: lux
    });

    // @ngInject
    function lux ($injector, $location, $window, $http, $log, $timeout,
                  $compile, $rootScope, luxMessage) {
        var core = {
            $injector: $injector,
            $location: $location,
            $window: $window,
            $http: $http,
            $log: $log,
            $timeout: $timeout,
            $compile: $compile,
            $rootScope: $rootScope,
            $require: require,
            require: _require,
            messages: luxMessage,
            context: windowContext($window),
            moduleLoaded: moduleLoaded
        };
        return new Lux(core, plugins);
    }


    function moduleLoaded (name) {
        try {
            _.module(name);
            return true;
        } catch (err) {
            return false;
        }
    }

    function unknownModules (modules) {
        var unknowns = [];
        if (!_.isArray(modules)) modules = [modules];
        _.forEach(modules, (name) => {
            if (!moduleLoaded(name)) unknowns.push(name);
        });
        return unknowns.length ? unknowns : null;
    }

    function _require(libNames, modules, onLoad) {
        var $lux = this;

        if (arguments.length === 2) {
            onLoad = modules;
            modules = null;
        }
        if (loading)
            return loadingQueue.push({
                libNames: libNames,
                modules: modules,
                onLoad: onLoad
            });

        if (!_.isArray(libNames)) libNames = [libNames];

        if (modules)
            modules = unknownModules(modules);

        $lux.$require(libNames, execute);

        function execute() {

            if (modules) loadModule(modules);

            onLoad.apply(null, arguments);

            $lux.$timeout(consumeQueue);
        }

        function consumeQueue() {
            var q = loadingQueue.splice(0, 1);
            if (q.length) {
                q = q[0];
                $lux.require(q.libNames, q.modules, q.onLoad);
            }
        }

        function loadModule(modules) {
            let moduleFunctions = [];

            const runBlocks = collectModules(modules, moduleCache, moduleFunctions, []);

            _.forEach(moduleFunctions, (moduleFn) => {
                try {
                    _invokeQueue(moduleFn._invokeQueue);
                    _invokeQueue(moduleFn._configBlocks);
                } catch (e) {
                    if (e.message) e.message += ' while loading ' + moduleFn.name;
                    throw e;
                }
            });

            function _invokeQueue(queue) {
                _.forEach(queue, (args) => {
                    var provider = providers[args[0]] || $injector.get(args[0]);
                    if (provider)
                        provider[args[1]].apply(provider, args[2]);
                    else
                        return $lux.$log.error("unsupported provider " + args[0]);
                });
            }

            _.forEach(runBlocks, (fn) => {
                $lux.$injector.invoke(fn);
            });
        }
    }
}


function collectModules(modules, cache, moduleFunctions, runBlocks) {
    let moduleFn;

    _.forEach(modules, (moduleName) => {
        if (!cache[moduleName]) {
            moduleFn = _.module(moduleName);
            cache[moduleName] = true;
            runBlocks = collectModules(moduleFn.requires, cache, moduleFunctions, runBlocks);
            moduleFunctions.push(moduleFn);
            runBlocks = runBlocks.concat(moduleFn._runBlocks);
        }
    });

    return runBlocks;
}
