import os
import hmac
import json
import hashlib

from pulsar.apps.wsgi import Json
from pulsar.utils.string import to_bytes
from pulsar import (HttpException, PermissionDenied, BadRequest,
                    as_coroutine)

from lux.core import Router


class GithubHook(Router):
    """A Router for handling Github webhooks
    """
    response_content_types = ['application/json']
    handle_payload = None
    secret = None

    async def post(self, request):
        data = await as_coroutine(request.body_data())

        if self.secret:
            try:
                self.validate(request)
            except HttpException:
                raise
            except Exception as exc:
                exc = str(exc)
                request.logger.exception(exc)
                raise BadRequest(exc)

        event = request.get('HTTP_X_GITHUB_EVENT')
        if self.handle_payload:
            try:
                data = await self.handle_payload(request, event, data)
            except HttpException:
                raise
            except Exception as exc:
                exc = str(exc)
                request.logger.exception(exc)
                raise BadRequest(exc)
        else:
            data = dict(success=True, event=event)
        return Json(data).http_response(request)

    def validate(self, request):
        hub_signature = request.get('HTTP_X_HUB_SIGNATURE')

        if not hub_signature:
            raise PermissionDenied('No signature')

        if '=' in hub_signature:
            sha_name, signature = hub_signature.split('=')
            if sha_name != 'sha1':
                raise PermissionDenied('Bad signature')
        else:
            raise BadRequest('bad signature')

        payload = request.get('wsgi.input').read()
        sig = github_signature(self.secret, payload)

        if sig.hexdigest() != signature:
            raise PermissionDenied('Bad signature')


class EventHandler:

    def __call__(self, request, event, data):
        raise NotImplementedError


class PullRepo(EventHandler):

    def __init__(self, repo):
        self.repo = repo

    async def __call__(self, request, event, data):
        app = request.app
        response = dict(success=True, event=event)
        if event == 'push':
            if os.path.isdir(self.repo):
                command = 'cd %s; git symbolic-ref --short HEAD' % self.repo
                branch = await app.shell(request, command)
                branch = branch.split('\n')[0]
                response['command'] = self.command(branch)
                result = await app.shell(request, response['command'])
                response['result'] = result
                await as_coroutine(app.reload())
            else:
                raise HttpException('Repo directory not valid', status=412)
        return response

    def command(self, branch):
        # git checkout HEAD path/to/your/dir/or/file
        return 'cd %s; git pull origin %s;' % (self.repo, branch)


def github_signature(secret, payload):
    secret = to_bytes(secret)
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    payload = to_bytes(payload)
    return hmac.new(secret, msg=payload, digestmod=hashlib.sha1)
