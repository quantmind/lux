"""Management utility to create superusers."""
import json
from copy import copy
from collections import OrderedDict as obj

from lux.core import LuxCommand
from lux.utils.text import engine


methods = ('get', 'head', 'post', 'patch', 'put', 'delete')


class Command(LuxCommand):
    help = 'Create Open API documents'

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

        for name, doc in docs.items():
            filename = '%s_spec.json' % name
            with open(filename, 'w') as fp:
                json.dump(doc, fp, indent=2)
                self.write('Created %s' % filename)

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

        return getattr(self, 'doc_%s' % verb)(method, parameters, model)

    def doc_get(self, method, parameters, model):
        doc = obj(model.json_docs.get("get") or ())
        if "description" not in doc:
            doc["description"] = (
                "Return a pagination object containing a list of %s"
                % engine.plural(model.name)
            )
        if parameters:
            doc['parameters'] = parameters
        return doc

    def doc_post(self, method, parameters, model):
        pass

    def doc_put(self, method, parameters, model):
        pass

    def doc_patch(self, method, parameters, model):
        pass

    def doc_head(self, method, parameters, model):
        doc = obj(model.json_docs.get("get") or ())
        if "description" not in doc:
            doc["description"] = ""
        if parameters:
            doc['parameters'] = parameters
        return doc

    def doc_delete(self, method, parameters, model):
        pass
