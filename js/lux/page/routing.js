
    //  ROUTING
    //  -----------------
    //
    //  Build an HTML5 sitemap when the ``context.sitemap`` variable is set.
    function _load_sitemap (hrefs, pages) {
        //
        forEach(hrefs, function (href) {
            var page = pages[href];
            if (page && page.href && page.target !== '_self') {
                lux.addRoute(page.href, route_config(page));
            }
        });
    }

    // Configure a route for a given page
    function route_config (page) {

        return {
            //
            // template url for the page
            templateUrl: page.template_url,
            //
            template: '<div ng-bind-html="page.content"></div>',
            //
            controller: page.controller || 'html5Page',
            //
            resolve: {
                response: function ($lux, $route) {
                    if (page.api) {
                        var api = $lux.api(page.api);
                        return api.get($route.current.params);
                    }
                }
            }
        };
    }
    //
    // Load sitemap if available
    _load_sitemap(context.hrefs, context.pages);
