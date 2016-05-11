import _ from '../ng';


// @ngInject
export default function ($controllerProvider, $provide, $compileProvider, $filterProvider) {

    var loading = false,
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
            if (!_.isArray(modules)) modules = [modules];

            if (!modules.length) {
                onLoad();
                return;
            }

            if (!_.isArray(libNames)) libNames= [libNames];

            if (loading)
                loadingQueue.push([libNames, modules, onLoad]);
            else {
                provider.$require(libNames, () => {
                    loadModule(modules, onLoad);
                });
            }
        }

        function consumeQueue() {
            var q = loadingQueue.splice(0, 1);
            if (q.length) {
                q = q[0];
                require(q[0], q[1], q[2]);
            }
        }

        function loadModule(modules, onLoad) {
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

            onLoad();
            $timeout(consumeQueue);
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
