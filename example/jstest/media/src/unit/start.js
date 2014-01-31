define(['lux-web', 'qunit'], function () {
    "use strict";
    var web = lux.web,
        test_destroy = function (instance) {
            var elem = instance.element(),
                ext = instance.extension(),
                id = instance.id();
            equal(ext.instance(instance), instance);
            equal(ext.instance(id), instance);
            instance.destroy();
            equal(ext.instance(id), undefined);
        };
    //

    var Todo1 = lux.Model.extend({
        meta: {
            name: 'todo1',
            attributes: {
                'title': null,
                'description': null,
                'when': lux.utils.asDate
            }
        }
    });


    var Todo2 = lux.Model.extend({
        meta: {
            name: 'todo2',
            attributes: {
                'title': null,
                'description': null,
                'when': lux.utils.asDate
            }
        }
    });