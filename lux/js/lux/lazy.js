import _ from '../ng';


// @ngInject
export default function ($controllerProvider, $provide, $compileProvider, $filterProvider) {

    var loading = false,
        slice = Array.prototype.slice,
        loadingQueue = [],
        providers = {
            $controllerProvider: $controllerProvider,
            $compileProvider: $compileProvider,
            $filterProvider: $filterProvider,
            $provide: $provide // other things
        };

    this.$get = getProvider;

    // @ngInject
    function getProvider ($injector, $log, $compile, $timeout) {
        var moduleCache = {};

        var provider = {
            require: _require,
            $require: require,
            $compile: $compile
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
            let moduleFunctions = [],
                provider,
                invokeQueue,
                invokeArgs,
                ii, i;

            const runBlocks = collectModules(modules, moduleCache, moduleFunctions, []);

            _.forEach(moduleFunctions, (moduleFn) => {
                try {
                    for (invokeQueue = moduleFn._invokeQueue, i = 0, ii = invokeQueue.length; i < ii; i++) {
                        invokeArgs = invokeQueue[i];

                        if (providers.hasOwnProperty(invokeArgs[0])) {
                            provider = providers[invokeArgs[0]];
                        } else {
                            return $log.error("unsupported provider " + invokeArgs[0]);
                        }
                        provider[invokeArgs[1]].apply(provider, invokeArgs[2]);
                    }
                } catch (e) {
                    if (e.message) e.message += ' while loading ' + moduleFn.name;
                    throw e;
                }
            });

            _.forEach(runBlocks, (fn) => {
                $injector.invoke(fn);
            });
        }
    }
}


function collectModules(modules, cache, moduleFunctions, runBlocks) {
    let moduleFn;

    _.forEach(modules, (name) => {
        if (!cache[name]) {
            moduleFn = _.module(name);
            cache[name] = true;
            runBlocks = collectModules(moduleFn.requires, cache, moduleFunctions, runBlocks);
            moduleFunctions.push(moduleFn);
            runBlocks = runBlocks.concat(moduleFn._runBlocks);
        }
    });

    return runBlocks;
}
