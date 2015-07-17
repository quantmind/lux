import os
import hmac
import asyncio

from pulsar.apps.wsgi import Json
from pulsar.utils.string import to_bytes
from pulsar import task, HttpException, PermissionDenied

import lux


class GithubHook(lux.Router):
    response_content_types = ['application/json']
    repo = None
    secret = None

    @task
    def post(self, request):
        data = request.body_data()

        if self.secret:
            secret = to_bytes(self.secret)
            signature = request.get('HTTP_X_HUB_SIGNATURE')
            if not signature:
                raise PermissionDenied('no signature')
            payload = request.get('wsgi.input').read()
            sig = hmac.new(secret, payload)
            if sig.hexdigest() != signature:
                raise PermissionDenied('bad signature')

        event = request.get('HTTP_X_GITHUB_EVENT')
        if event == 'push':
            if self.repo and os.path.isdir(self.repo):
                yield from asyncio.create_subprocess_shell(self.command())
            else:
                raise HttpException('Repo directory not valid', status=412)

        return Json(dict(success=True)).http_response(request)

    def command(self):
        return 'cd %s; git pull origin master' % self.repo

