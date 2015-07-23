    angular.module('lux.cms', [
        'lux.cms.core',
        'lux.cms.component.text'])

    .run(['$rootScope', 'CMS', function(scope, CMS) {

        scope.cms = new CMS();
    }])

    .factory('CMS', ['Component', function(Component) {

        var CMS = function CMS() {
            var self = this;

            self.components = new Component(self);
        };

        return CMS;
    }]);
