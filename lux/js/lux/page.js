// @ngInject
export default function ($lux) {
    var checked = 0;

    return {
        restrict: 'A',
        link: {
            post: function (scope, element) {
                // TODO this is broken
                element.addClass('lux');
                scope.$on('lux-ready', () => {
                    element.addClass('lux');
                });
                $lux.$timeout(check);
                if ($lux.user) element.addClass('auth');
                else element.addClass('anonymous');
                if ($lux.context.page)
                    element.addClass($lux.context.page.slug);
            }
        }
    };

    function check () {
        // Lux has done with bootstrapping
        if (!$lux.bootstrap()) return;
        // removed the bootstrap call above
        if (!$lux.bootstrapDone()) {
            checked++;
            if (checked > 5) $lux.bootstrapDone(true);
            else $lux.$timeout(check, 1);
        }
    }
}
