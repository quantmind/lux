from lux.utils import test
from lux.ext.rest import DictModel


class TestDictModel(test.TestCase):
    config_file = 'tests.rest'

    def test_instance(self):
        model = DictModel('test', fields=('id', 'foo', 'name'))
        self.assertDictEqual(model.create_instance(), {})
        o = model.instance()
        model.set_instance_value(o, 'foo', 'bla')
        self.assertEqual(model.get_instance_value(o, 'foo'), 'bla')
        model.set_instance_value(o, 'xxx', 'bla')
        self.assertEqual(model.get_instance_value(o, 'xxx'), None)
        self.assertEqual(len(model.fields()), 5)

    def test_json(self):
        model = DictModel('test', fields=('id', 'foo', 'name'))
        app = self.application()
        app.models.register(model)
        request = app.wsgi_request()
        o = model.instance()
        model.set_instance_value(o, 'id', 1)
        model.set_instance_value(o, 'name', 'pippo')
        data = model.tojson(request, o)
        self.assertEqual(len(data), 2)
        model.set_instance_value(o, 'name', None)
        data = model.tojson(request, o)
        self.assertEqual(len(data), 1)
