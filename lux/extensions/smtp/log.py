import logging
import json
from asyncio import async

from pulsar.apps.http import HttpClient
from pulsar.utils.log import lazymethod


class SMTPHandler(logging.Handler):

    def __init__(self, app, level):
        super().__init__(logging._checkLevel(level))
        self.app = app

    def emit(self, record):
        cfg = self.app.config
        managers = cfg['SITE_MANAGERS']
        if getattr(record, 'mail', False) or not managers:
            return
        backend = self.app.email_backend
        msg = self.format(record)
        first = record.message.split('\n')[0]
        subject = '%s - %s - %s' % (cfg['APP_NAME'], record.levelname, first)
        backend.send_mail(to=managers,
                          subject=subject,
                          message=msg)


class SlackHandler(logging.Handler):
    """Handler that will emit every event to slack channel
    """
    webhook_url = 'https://hooks.slack.com/services'

    def __init__(self, app, level, token):
        super().__init__(logging._checkLevel(level))
        self.app = app
        self.webhook_url = '%s/%s' % (self.webhook_url, token)

    @lazymethod
    def http(self):
        return HttpClient()

    def emit(self, record):
        """Emit record to slack channel using pycurl to avoid recurrence
        event logging (log logged record)
        """
        data = dict(text="```\n%s\n```" % self.format(record))
        http = self.http()
        async(http.post(self.webhook_url, data=json.dumps(data)),
              loop=http._loop)
