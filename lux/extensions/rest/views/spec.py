import os

from lux.core import JsonRouter

from pulsar import Http404

from lux.core import cached, GET_HEAD

# from swagger_spec_validator.validator20 import validate_spec


class Specification(JsonRouter):
    """
    Single API that corresponds to a flask blueprint
    """
    def get(self, request):
        return self.json_response(request, specification(request))

    def options(self, request):
        request.app.fire('on_preflight', request, methods=GET_HEAD)
        return request.response


@cached
def specification(request):
    """Load yaml specification
    """
    import yaml
    app = request.app
    url = request.config.get('API_DOCS_YAML_URL')
    if not url:
        raise Http404
    if url.startswith('http'):
        http = app.http()
        response = http.get(url)
        if response.status_code != 200:
            request.logger.error('Could not load yaml file from %s: %s' % url,
                                 response.status_code)
            raise Http404
        spec = response.text()
    elif os.path.isfile(url):
        with open(url, 'r') as fp:
            spec = fp.read()
    else:
        raise Http404

    rnd = app.template_engine()
    context = dict(request.config)
    context['version'] = request.app.get_version()
    spec = rnd(spec, context)
    spec = yaml.safe_load(spec)
    spec['host'] = request.get_host()
    spec['schemes'] = [request.scheme]
    # validate_spec(spec)
    return spec
