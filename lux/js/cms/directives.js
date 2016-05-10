import _ from '../ng';


export function luxMessages () {

    return {
        restrict: 'AE',
        replace: true,
        scope: {},
        template: messageTpl,
        link: messages
    };

    function pushMessage(scope, message) {
        message.type = message.level;
        if (message.type === 'error') message.type = 'danger';
        scope.messages.push(message);
    }

    function messages ($scope) {
        $scope.messages = [];

        $scope.removeMessage = function ($event, message) {
            $event.preventDefault();
            var msgs = $scope.messages;
            for (var i = 0; i < msgs.length; ++i) {
                if (msgs[i].$$hashKey === message.$$hashKey)
                    msgs.splice(i, 1);
            }
        };

        $scope.$on('messageAdded', function (e, message) {
            if (!e.defaultPrevented) pushMessage($scope, message);
        });

        $scope.$on('messageRemove', function (e, id) {
            var messages = [];

            if (id)
                _.forEach($scope.messages, (m) => {
                    if (m.id !== id) messages.push(m);
                });

            $scope.messages = messages;
        });
    }
}


const messageTpl = `<div>
    <div class="alert alert-{{ message.type }}" role="alert" ng-repeat="message in messages">
        <a href="#" class="close" ng-click="removeMessage($event, message)">&times;</a>
        <i ng-if="message.icon" ng-class="message.icon"></i>
        <span ng-bind-html="message.text"></span>
    </div>
</div>`
