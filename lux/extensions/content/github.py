import os
import hmac
import hashlib
import asyncio

from pulsar.apps.wsgi import Json
from pulsar.utils.string import to_bytes
from pulsar import task, HttpException, PermissionDenied, BadRequest

import lux


class GithubHook(lux.Router):
    response_content_types = ['application/json']
    repo = None
    secret = None

    @task
    def post(self, request):
        data = request.body_data()

        if self.secret:
            try:
                self.validate(request)
            except Exception as exc:
                if hasattr(exc, 'status'):
                    raise
                else:
                    raise BadRequest

        event = request.get('HTTP_X_GITHUB_EVENT')
        data = self.handle_payload(request, event, data)
        return Json(data).http_response(request)

    def handle_payload(self, request, event, data):
        response = dict(success=True, event=event)
        if event == 'push':
            if self.repo and os.path.isdir(self.repo):
                response['command'] = self.command()
                yield from asyncio.create_subprocess_shell(response['command'])
            else:
                raise HttpException('Repo directory not valid', status=412)

        return response

    def validate(self, request):
        secret = to_bytes(self.secret)
        hub_signature = request.get('HTTP_X_HUB_SIGNATURE')

        if not hub_signature:
            raise PermissionDenied('No signature')

        sha_name, signature = hub_signature.split('=')
        if sha_name != 'sha1':
            raise PermissionDenied('Bad signature')

        payload = request.get('wsgi.input').read()
        sig = hmac.new(secret, msg=payload, digestmod=hashlib.sha1)

        if sig.hexdigest() != signature:
            raise PermissionDenied('Bad signature')

    def command(self):
        # git checkout HEAD path/to/your/dir/or/file
        return 'cd %s; git fetch; git checkout HEAD' % self.repo
