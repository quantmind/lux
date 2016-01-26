define(['angular',
        'lux',
        'lux/testing',
        'lux/components/fileupload'], function (angular, lux, tests) {
    'use strict';

    describe('Test lux.components.fileupload', function () {

        beforeEach(function () {
            module('lux.form.fileupload');
        });

        it('adds the ngf-select directive',
            inject(function ($compile, $rootScope) {
                lux.formFieldTests.file = tests.createForm([{
                    type: 'file',
                    name: 'file'
                }]);
                var element = tests.digest($compile, $rootScope,
                    '<div><lux-form data-options="lux.formFieldTests.file"></lux-form></div>'),
                    form = element.children();
                //
                expect(form.children().length).toBe(1);
                //
                var tags = form.children().children();
                expect(tags[0].tagName).toBe('LABEL');
                expect(tags[1].tagName).toBe('INPUT');
                expect(tags[1].getAttribute('type')).toBe('file');
                expect(tags[1].hasAttribute('ngf-select')).toBeTruthy();
                //
            })
        );

        it('doesnt adds the ngf-select directive',
            inject(function ($compile, $rootScope) {
                lux.formFieldTests.fileNoNgf = tests.createForm([{
                    type: 'file',
                    name: 'file'
                }], {useNgFileUpload: false});
                var element = tests.digest($compile, $rootScope,
                    '<div><lux-form data-options="lux.formFieldTests.fileNoNgf"></lux-form></div>'),
                    form = element.children();
                //
                expect(form.children().length).toBe(1);
                //
                var tags = form.children().children();
                expect(tags[0].tagName).toBe('LABEL');
                expect(tags[1].tagName).toBe('INPUT');
                expect(tags[1].getAttribute('type')).toBe('file');
                expect(tags[1].hasAttribute('ngf-select')).toBeFalsy();
                //
            })
        );
    });

});
