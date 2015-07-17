import os
import asyncio

import lux


class GithubHook(lux.Router):
    repo = None

    def post(self, request):
        if self.repo and os.path.isdir(self.repo):
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.update_code, request)
        else:
            request.logger.warning('Repo directory not valid')

    def update_code(self, request):
        pass
