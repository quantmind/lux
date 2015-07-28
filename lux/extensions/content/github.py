import os
import hmac
import hashlib
from asyncio import create_subprocess_shell, subprocess

from pulsar.apps.wsgi import Json
from pulsar.utils.string import to_bytes
from pulsar import task, HttpException, PermissionDenied, BadRequest

import lux


class GithubHook(lux.Router):
    '''A Router for handling Github webhooks
    '''
    response_content_types = ['application/json']
    handle_payload = None
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
        if self.handle_payload:
            data = yield from self.handle_payload(request, event, data)
        else:
            data = dict(success=True, event=event)
        return Json(data).http_response(request)

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


class EventHandler:

    def __call__(self, request, event, data):
        raise NotImplementedError

    def execute(self, command):
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
                branch, e = yield from self.execute(command)
                if e:
                    raise HttpException(e, status=412)
                branch = branch.split('\n')[0]
                response['command'] = self.command(branch)
                result, e = yield from self.execute(response['command'])
                response['result'] = result
                response['error'] = e
            else:
                raise HttpException('Repo directory not valid', status=412)
        return response

    def command(self, branch):
        # git checkout HEAD path/to/your/dir/or/file
        return 'cd %s; git pull origin %s;' % (self.repo, branch)
