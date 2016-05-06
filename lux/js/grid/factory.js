import _ from '../ng';
import {jslib} from '../core/utils';


// @ngInject
export default function ($window, luxGridConfig) {

    return luxGridApi;

    function luxGridApi (scope, options) {
        options = _.extend({}, luxGridConfig.defaults, options);
        var grid = new Grid(options, luxGridConfig);
        grid.dataProvider = luxGridConfig.getDataProvider(grid);
        grid.dataProvider.connect();
        return grid;
    }
}


class Grid {

    constructor (options, cfg) {
        var self = this;
        this.options = options;
        this.cfg = cfg;

        options.onRegisterApi = function (api) {
            if (!jslib('lodash')) {
                jslib('lodash', () => {
                    self.onRegisterApi(api);
                });
            } else
                self.onRegisterApi(api);
        };
    }

    onRegisterApi (api) {
        this.options = api.grid.options;
        this.api = api;
        api.lux = this;
        this.cfg.onInit(this);
        this.dataProvider.getPage();
    }

}
