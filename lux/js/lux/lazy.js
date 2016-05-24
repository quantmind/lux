import _ from '../ng';


// @ngInject
export default function ($controllerProvider, $provide, $compileProvider, $filterProvider,
                         $locationProvider, $injector) {

    var loading = false,
        loadingQueue = [],
        providers = {
            $controllerProvider: $controllerProvider,
            $compileProvider: $compileProvider,
            $filterProvider: $filterProvider,
            $provide: $provide, // other things (constant, decorator, provider, factory, service)
            $injector: $injector
        };

    this.$get = getProvider;

    $locationProvider.html5Mode({
        enabled: true,
        requireBase: false,
        rewriteLinks: false
    });

    // @ngInject
    function getProvider ($injector, $log, $compile, $timeout, $rootScope) {
        var moduleCache = {};

        var provider = {
            require: _require,      // require with module loading
            $require: require,      // requirejs
            $compile: $compile,
            $rootScope: $rootScope
        };

        return provider;

        function _require(libNames, modules, onLoad) {
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

            provider.$require(libNames, execute);

            function execute() {

                if (modules) loadModule(modules);

                onLoad.apply(null, arguments);

                $timeout(consumeQueue);
            }
        }

        function consumeQueue() {
            var q = loadingQueue.splice(0, 1);
            if (q.length) {
                q = q[0];
                provider.require(q.libNames, q.modules, q.onLoad);
            }
        }

        function loadModule(modules) {
            if (!_.isArray(modules)) modules = [modules];
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

            function _invokeQueue (queue) {
                _.forEach(queue, (args) => {
                    var provider = providers[args[0]],
                        method = args[1];
                    if (provider)
                        provider[method].apply(provider, args[2]);
                    else
                        return $log.error("unsupported provider " + args[0]);
                });
            }

            _.forEach(runBlocks, (fn) => {
                $injector.invoke(fn);
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
