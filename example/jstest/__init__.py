from pulsar.apps.ws import WebSocket

import lux
from lux import route, Html
from lux.extensions import api

from .ui import add_css


template = '''
<h1 id="qunit-header">Lux Test Suite</h1>
 <h2 id="qunit-banner"></h2>
 <div id="qunit-testrunner-toolbar"></div>
 <h2 id="qunit-userAgent"></h2>
 <ol id="qunit-tests"></ol>
 <div id="qunit-fixture">test markup, will be hidden</div>'''


class JsTests(lux.Router):

    @route('/unit')
    def unit(self, request):
        html = request.html_document
        html.head.scripts.require('cms')
        html.head.scripts.require('qunit')
        html.head.scripts.require('jstest/unit.js')
        html.head.links.append('qunit-css')
        html.body.append(template)
        return html.http_response(request)

    @route('/bench')
    def bench(self, request):
        html = request.html_document
        scripts = html.head.scripts
        scripts.require('cms')
        scripts.require('node_modules/benchmark/benchmark.js')
        scripts.require('jstest/bench.js')
        return html.http_response(request)

    @route('/visual')
    def visual(self, request):
        doc = request.html_document
        scripts = doc.head.scripts
        scripts.require('jstest/visual.js')
        return Html('div', cn='visual-test').http_response(request)


class TestSocket(api.CrudWebSocket):

    def ping(self, websocket, message):
        message['data'] = 'pong'
        self.write(websocket, message)


class Extension(lux.Extension):

    def middleware(self, app):
        return[JsTests('jstests', WebSocket('socket', TestSocket()))]
