angular.module('templates-message', ['message/message.tpl.html']);

angular.module("message/message.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("message/message.tpl.html",
    "<div>\n" +
    "    <div class=\"alert alert-{{ message.type }}\" role=\"alert\" ng-repeat=\"message in messages\">\n" +
    "        <a href=\"#\" class=\"close\" ng-click=\"removeMessage($event, message)\">&times;</a>\n" +
    "        <i ng-if=\"message.icon\" ng-class=\"message.icon\"></i>\n" +
    "        <span ng-bind-html=\"message.text\"></span>\n" +
    "    </div>\n" +
    "</div>\n" +
    "");
}]);
