import os
import hmac
import hashlib
from asyncio import create_subprocess_shell, subprocess

from pulsar.apps.wsgi import Json
from pulsar.utils.string import to_bytes
from pulsar import HttpException, PermissionDenied, BadRequest

import lux


class GithubHook(lux.Router):
    '''A Router for handling Github webhooks
    '''
    response_content_types = ['application/json']
    handle_payload = None
    secret = None

    def post(self, request):
        data = request.body_data()

        if self.secret:
            try:
                self.validate(request)
            except Exception as exc:
                if hasattr(exc, 'status'):
                    raise
                else:
                    exc = str(exc)
                    request.logger.exception(exc)
                    raise BadRequest(exc)

        event = request.get('HTTP_X_GITHUB_EVENT')
        if self.handle_payload:
            data = self.handle_payload(request, event, data)
        else:
            data = dict(success=True, event=event)
        return Json(data).http_response(request)

    def validate(self, request):
        secret = to_bytes(self.secret)
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
        sig = hmac.new(secret, msg=payload, digestmod=hashlib.sha1)

        if sig.hexdigest() != signature:
            raise PermissionDenied('Bad signature')


class EventHandler:

    def __call__(self, request, event, data):
        raise NotImplementedError

    def execute(self, request, command):
        green_pool = request.app.green_pool
        if green_pool:
            return green_pool.wait(self._async_execute(command))
        else:
            return self._sync_execute(command)

    def _sync_execute(self, command):
        raise NotImplementedError

    def _async_execute(self, command):
        p = yield from create_subprocess_shell(command,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
        b, e = yield from p.communicate()
        return b.decode('utf-8'), e.decode('utf-8')


class PullRepo(EventHandler):

    def __init__(self, repo):
        self.repo = repo

    def __call__(self, request, event, data):
        response = dict(success=True, event=event)
        if event == 'push':
            if os.path.isdir(self.repo):
                command = 'cd %s; git symbolic-ref --short HEAD' % self.repo
                branch, e = self.execute(request, command)
                if e:
                    raise HttpException(e, status=412)
                branch = branch.split('\n')[0]
                response['command'] = self.command(branch)
                result, e = self.execute(request, response['command'])
                response['result'] = result
                response['error'] = e
            else:
                raise HttpException('Repo directory not valid', status=412)
        return response

    def command(self, branch):
        # git checkout HEAD path/to/your/dir/or/file
        return 'cd %s; git pull origin %s;' % (self.repo, branch)
