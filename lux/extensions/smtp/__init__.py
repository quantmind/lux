import logging

import lux
from lux import Parameter

from .backend import EmailBackend


__all__ = ['EmailBackend']


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
        Parameter('SMTP_LOG_LEVEL', None, 'Logging level for email messages')
    ]

    def on_start(self, app, server):
        level = app.config['SMTP_LOG_LEVEL']
        if level:
            smtp = SMTPLogger(app, level)
            root = logging.getLogger('')
            root.addHandler(smtp)
            for logger in root.manager.loggerDict.values():
                if (isinstance(logger, logging.Logger) and
                        not logger.propagate and logger.handlers):
                    logger.addHandler(smtp)


class SMTPLogger(logging.Handler):

    def __init__(self, app, level):
        super().__init__(logging._checkLevel(level))
        self.app = app

    def emit(self, record):
        if getattr(record, 'mail', False):
            return
        cfg = self.app.config
        backend = self.app.email_backend
        msg = self.format(record)
        first = record.message.split('\n')[0]
        subject = '%s - %s - %s' % (cfg['APP_NAME'], record.levelname, first)
        backend.send_mail(to=cfg['SITE_MANAGERS'],
                          subject=subject,
                          message=msg)
