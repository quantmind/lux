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

        return {
            require: _require,
            $compile: $compile
        };

        function _require(libNames, modules, onLoad) {
            if (!_.isArray(modules)) modules = [modules];
            var missingModules = [];

            _.forEach(modules, (module) => {
                try {
                    _.module(module);
                } catch (err) {
                    missingModules.push(module);
                }
            });

            if (!missingModules.length) {
                onLoad();
                return;
            }

            if (!_.isArray(libNames)) libNames= [libNames];

            if (loading)
                loadingQueue.push([libNames, missingModules, onLoad]);
            else {
                require(libNames, () => {
                    loadModule(missingModules, onLoad);
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
            let runBlocks = [],
                provider,
                invokeQueue,
                invokeArgs,
                ii, i;

            for (let k = 0; k < modules.length; ++k) {

                const moduleName = modules[k];

                if (moduleCache[moduleName]) continue;

                const moduleFn = _.module(moduleName);

                runBlocks = runBlocks.concat(moduleFn._runBlocks);
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
                    if (e.message) e.message += ' while loading ' + moduleName;
                    throw e;
                }
            }

            _.forEach(runBlocks, (fn) => {
                $injector.invoke(fn);
            });

            _.forEach(modules, (module) => {
                moduleCache[module] = true;
            });

            onLoad();
            $timeout(consumeQueue);
        }
    }
}
