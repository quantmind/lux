require([
    'lux'
], function(lux) {
    "use strict";

    var $project_name = {};

    window.$project_name = $project_name;

    lux.bootstrap('$project_name', []);

    return $project_name;
});
