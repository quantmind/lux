angular.module('lux.cms', [
    'lux.cms.mock',
    'lux.cms.core',
    'lux.cms.component',
    'lux.cms.component.text'])

.run(function($rootScope, CMS) {
    $rootScope.cms = new CMS();
})

.factory('CMS', ['Component', function(Component) {
    var CMS = function CMS() {
        var self = this;

        self.components = new Component(self);
    };

    return CMS;
}]);
