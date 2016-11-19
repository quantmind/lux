"""Management utility to swagger docs for API

check also

http://hirelofty.com/blog/auto-generate-swagger-docs-your-django-api/
"""
import json
from copy import copy
from collections import OrderedDict as obj

from pulsar.utils.structures import mapping_iterator

from lux import forms
from lux.core import LuxCommand
from lux.forms import get_form_class


methods = ('get', 'head', 'post', 'patch', 'put', 'delete')


class Command(LuxCommand):
    help = 'Create Open API JSON document'

    def run(self, options):
        docs = obj()
        default = self.app.config['APP_NAME'].lower()

        for api in self.app.apis:
            if api.netloc:
                continue

            for router in api.router.routes:
                model = router.model
                spec = default
                if model and model.spec:
                    spec = model.spec.lower()

                if spec not in docs:
                    docs[spec] = self.doc()

                spec = docs[spec]
                self.get_routes(router, model, spec["paths"])

        files = []
        for name, doc in docs.items():
            filename = '%s_spec.json' % name
            with open(filename, 'w') as fp:
                json.dump(doc, fp, indent=2)
                self.write('Created %s' % filename)
                files.append(filename)
        return files

    def get_routes(self, router, model, paths):
        verbs = obj()

        parameters = []
        route = router.route
        bits = []
        for is_dynamic, val in route.breadcrumbs:
            if is_dynamic:
                parameters.append(obj((
                    ("name", val),
                    ("description", ""),
                    ("type", "string"),
                    ("required", True),
                    ("in", "path")
                )))
                val = '{%s}' % val
            bits.append(val)
        path = '/%s' % ('/'.join(bits))

        for verb in methods:
            method = getattr(router, verb, None)
            if hasattr(method, '__call__'):
                doc = self.describe(router, verb, method, parameters, model)
                if doc:
                    verbs[verb] = doc

        if verbs:
            paths[path] = verbs

        for child in router.routes:
            self.get_routes(child, model, paths)

    def doc(self):
        return obj((
            ("swagger", "2.0"),
            ("info", obj(
                version="",
                title="",
                description=""
            )),
            ("produces", [
                "application/json"
            ]),
            ("paths", obj())
        ))

    def describe(self, router, verb, method, parameters, model):
        if not model:
            doc = obj(description=method.__doc__)
            responses = getattr(method, 'responses', None)
            if responses:
                doc['responses'] = copy(responses)
            return doc

        return self.model_doc(verb, method, parameters, model)

    def model_doc(self, verb, method, parameters, model):
        doc = obj(model.json_docs.get(verb) or ())
        if "description" not in doc:
            doc["description"] = trim_docstring(method.__doc__)
        parameters = self.method_parameters(verb, method, parameters, model)
        if parameters:
            doc['parameters'] = parameters
        responses = getattr(method, 'responses', None)
        if responses:
            doc["responses"] = dict(method_responses(responses))
        return doc

    def method_parameters(self, verb, method, parameters, model):
        form = get_form_class(self.app, getattr(method, 'form', None))
        if not form:
            if verb == 'post':
                form = get_form_class(self.app, model.form)
            elif verb == 'patch':
                form = get_form_class(self.app, model.updateform)

        if form:
            parameters = (parameters or [])[:]
            for name, field in form.base_fields.items():
                parameters.append(obj((
                    ("name", name),
                    ("description", field.help_text or field.label or name),
                    ("type", field_type(field)),
                    ("required", field.required),
                    ("in", "formData")
                )))
        return parameters


def trim_docstring(doc):
    if not doc:
        return ""
    lines = []
    for line in doc.split('\n'):
        lines.append(line.strip())
    return '\n'.join(lines)


def method_responses(responses):
    for code, info in mapping_iterator(responses):
        if isinstance(info, str):
            info = obj(description=info)
        yield code, info


def field_type(field):
    if isinstance(field, forms.FloatField):
        type = "number"
    elif isinstance(field, forms.IntegerField):
        type = "integer"
    elif isinstance(field, forms.BooleanField):
        type = "boolean"
    else:
        type = "string"
    return type
