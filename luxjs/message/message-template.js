angular.module('templates-message', ['message/message.tpl.html']);

angular.module("message/message.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("message/message.tpl.html",
    "<div>\n" +
    "    <div class=\"alert alert-{{ message.type }}\" role=\"alert\" ng-repeat=\"message in messages  track by $index | limitTo: limit\" ng-if=\"! ( !debug()  && message.type === 'warning' ) \">\n" +
    "        <a href=\"#\" class=\"close\" ng-click=\"removeMessage(message)\">&times;</a>\n" +
    "        {{ message.text }}\n" +
    "    </div>\n" +
    "</div>\n" +
    "");
}]);
