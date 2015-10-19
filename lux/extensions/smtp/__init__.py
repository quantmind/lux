import logging

import lux
from lux import Parameter

from .backend import EmailBackend
from .views import ContactRouter
from .log import SMTPHandler, SlackHandler


__all__ = ['EmailBackend', 'ContactRouter']


class Extension(lux.Extension):

    _config = [
        # Override default email backend
        Parameter('EMAIL_BACKEND', 'lux.extensions.smtp.EmailBackend',
                  'Default email backend'),
        Parameter('EMAIL_HOST', '', 'SMTP email host'),
        Parameter('EMAIL_PORT', 465, 'SMTP email port'),
        Parameter('EMAIL_HOST_USER', '', 'SMTP email host user'),
        Parameter('EMAIL_HOST_PASSWORD', '', 'SMTP email host user password'),
        Parameter('EMAIL_TIMEOUT', None, 'timeout for email timeout'),
        Parameter('EMAIL_USE_TLS', False, 'use TLS when using SMTP email'),
        Parameter('EMAIL_TLS_KEYFILE', None, 'TLS Keyfile'),
        Parameter('EMAIL_TLS_CERTFILE', None, 'TLS cert file'),
        Parameter('ENQUIRY_EMAILS', [],
                  'List of email messages to be sent on reception of enquiry'),
        Parameter('SMTP_LOG_LEVEL', None,
                  'Logging level for slack messages'),
        Parameter('SLACK_LOG_LEVEL', 'ERROR',
                  'Logging level for slack messages'),
        Parameter('SLACK_LOG_TOKEN', None,
                  'Token for posting messages to slack channel')
    ]

    def on_start(self, app, server):
        handlers = []
        level = app.config['SMTP_LOG_LEVEL']
        if level:
            handlers.append(SMTPHandler(app, level))
        level = app.config['SLACK_LOG_LEVEL']
        token = app.config['SLACK_LOG_TOKEN']
        if level and token:
            handlers.append(SlackHandler(app, level, token))
        if handlers:
            root = logging.getLogger('')
            self._add_handlers(root, handlers)
            for logger in root.manager.loggerDict.values():
                if (isinstance(logger, logging.Logger) and
                        not logger.propagate and logger.handlers):
                    self._add_handlers(logger, handlers)

    def _add_handlers(self, logger, handlers):
        for hnd in handlers:
            logger.addHandler(hnd)
