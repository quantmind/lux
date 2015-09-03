angular.module('templates-grid', ['grid/templates/modal.columns.tpl.html', 'grid/templates/modal.delete.tpl.html', 'grid/templates/modal.empty.tpl.html', 'grid/templates/modal.record.details.tpl.html']);

angular.module("grid/templates/modal.columns.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("grid/templates/modal.columns.tpl.html",
    "<div class=\"modal\" tabindex=\"-1\" role=\"dialog\" aria-hidden=\"true\">\n" +
    "  <div class=\"modal-dialog\">\n" +
    "    <div class=\"modal-content\">\n" +
    "      <div class=\"modal-header\" >\n" +
    "        <button type=\"button\" class=\"close\" aria-label=\"Close\" ng-click=\"$hide()\"><span aria-hidden=\"true\">&times;</span></button>\n" +
    "        <h4 class=\"modal-title\"><i class=\"fa fa-eye\"></i> Change columns visibility</h4>\n" +
    "      </div>\n" +
    "      <div class=\"modal-body\">\n" +
    "        <p class=\"modal-info\">{{infoMessage}}</p>\n" +
    "        <ul class=\"modal-items list-inline\">\n" +
    "          <li ng-repeat=\"col in columns\">\n" +
    "            <a class=\"btn btn-default\" ng-class=\"activeClass(col)\" ng-click=\"toggleVisible(col)\">{{col.displayName}}</a>\n" +
    "          </li>\n" +
    "        </ul>\n" +
    "      </div>\n" +
    "      <div class=\"modal-footer\">\n" +
    "        <button type=\"button\" class=\"btn btn-default\" ng-click=\"$hide()\">Close</button>\n" +
    "      </div>\n" +
    "    </div>\n" +
    "  </div>\n" +
    "</div>\n" +
    "");
}]);

angular.module("grid/templates/modal.delete.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("grid/templates/modal.delete.tpl.html",
    "<div class=\"modal\" tabindex=\"-1\" role=\"dialog\" aria-hidden=\"true\">\n" +
    "  <div class=\"modal-dialog\">\n" +
    "    <div class=\"modal-content\">\n" +
    "      <div class=\"modal-header\" >\n" +
    "        <button type=\"button\" class=\"close\" aria-label=\"Close\" ng-click=\"$hide()\"><span aria-hidden=\"true\">&times;</span></button>\n" +
    "        <h4 class=\"modal-title\"><i class=\"fa fa-trash\"></i> Delete {{stateName}}</h4>\n" +
    "      </div>\n" +
    "      <div class=\"modal-body\">\n" +
    "        <p class=\"modal-info\">{{infoMessage}}</p>\n" +
    "        <ul class=\"modal-items\">\n" +
    "          <li ng-repeat=\"item in selected\">{{item[repr_field]}}</li>\n" +
    "        </ul>\n" +
    "        <p class=\"text-danger cannot-undo\">{{dangerMessage}}</p>\n" +
    "      </div>\n" +
    "      <div class=\"modal-footer\">\n" +
    "        <button type=\"button\" class=\"btn btn-default\" ng-click=\"$hide()\">No</button>\n" +
    "        <button type=\"button\" class=\"btn btn-primary\" ng-click=\"ok()\">Yes</button>\n" +
    "      </div>\n" +
    "    </div>\n" +
    "  </div>\n" +
    "</div>\n" +
    "");
}]);

angular.module("grid/templates/modal.empty.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("grid/templates/modal.empty.tpl.html",
    "<div class=\"modal\" tabindex=\"-1\" role=\"dialog\" aria-hidden=\"true\">\n" +
    "  <div class=\"modal-dialog\">\n" +
    "    <div class=\"modal-content\">\n" +
    "      <div class=\"modal-header\">\n" +
    "        <button type=\"button\" class=\"close\" aria-label=\"Close\" ng-click=\"$hide()\"><span aria-hidden=\"true\">&times;</span></button>\n" +
    "        <h4 class=\"modal-title\"><i class=\"fa fa-trash\"></i> Lack of {{stateName}} to delete</h4>\n" +
    "      </div>\n" +
    "      <div class=\"modal-body\">\n" +
    "        <p class=\"modal-info\">{{emptyMessage}}</p>\n" +
    "      </div>\n" +
    "      <div class=\"modal-footer\">\n" +
    "        <button type=\"button\" class=\"btn btn-default\" ng-click=\"$hide()\">Close</button>\n" +
    "      </div>\n" +
    "    </div>\n" +
    "  </div>\n" +
    "</div>\n" +
    "");
}]);

angular.module("grid/templates/modal.record.details.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("grid/templates/modal.record.details.tpl.html",
    "<div class=\"modal\" tabindex=\"-1\" role=\"dialog\" aria-hidden=\"true\">\n" +
    "    <div class=\"modal-dialog record-details\">\n" +
    "        <div class=\"modal-content\">\n" +
    "            <div class=\"modal-header\" ng-show=\"title\">\n" +
    "                <button type=\"button\" class=\"close\" aria-label=\"Close\" ng-click=\"$hide()\">\n" +
    "                    <span aria-hidden=\"true\">&times;</span>\n" +
    "                </button>\n" +
    "                <h4 class=\"modal-title\" ng-bind=\"title\"></h4>\n" +
    "            </div>\n" +
    "            <div class=\"modal-body\" >\n" +
    "                <pre ng-bind=\"content\"></pre>\n" +
    "            </div>\n" +
    "            <div class=\"modal-footer\">\n" +
    "                <button type=\"button\" class=\"btn btn-default\" ng-click=\"$hide()\">Close</button>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</div>\n" +
    "");
}]);
