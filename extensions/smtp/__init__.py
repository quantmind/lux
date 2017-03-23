import logging

from lux.core import Parameter, LuxExtension

from .backend import EmailBackend
from .views import ContactRouter
from .log import SMTPHandler, SlackHandler


__all__ = ['EmailBackend', 'ContactRouter']


class Extension(LuxExtension):

    _config = [
        # Override default email backend
        Parameter('EMAIL_BACKEND', 'lux.extensions.smtp.EmailBackend',
                  'Default email backend'),
        Parameter('EMAIL_HOST', '', 'SMTP email host'),
        Parameter('EMAIL_PORT', 465, 'SMTP email port'),
        Parameter('EMAIL_HOST_USER', '', 'SMTP email host user'),
        Parameter('EMAIL_HOST_PASSWORD', '', 'SMTP email host user password'),
        Parameter('EMAIL_USE_TLS', True, 'use TLS when using SMTP email'),
        Parameter('EMAIL_TLS_KEYFILE', None, 'TLS Keyfile'),
        Parameter('EMAIL_TLS_CERTFILE', None, 'TLS cert file'),
        Parameter('EMAIL_SUPPORT', '',
                  'email address for support queries', True),
        Parameter('EMAIL_CAREERS', '',
                  'email address for support queries', True),
        Parameter('EMAIL_ENQUIRY_RESPONSE', [],
                  'List of email messages to be sent on reception of enquiry'),
        Parameter('EMAIL_MESSAGE_SUCCESS',
                  'Your message was sent! Thank You for your interest'),
        Parameter('SMTP_LOG_LEVEL', None,
                  'Logging level for email messages'),
        Parameter('SLACK_LOG_LEVEL', 'ERROR',
                  'Logging level for slack messages'),
        Parameter('SLACK_LOG_TOKEN', None,
                  'Token for posting messages to slack channel'),
        Parameter('SLACK_LINK_NAMES', None,
                  'Usernames to include as mention in the slack message'),
        Parameter('LOG_CONTEXT_FACTORY', None,
                  'Callable returning dict with system context for logging'),
        Parameter('CONTACT_US_URL', 'contact',
                  'Contact us url. Set to None if not needed')
    ]

    def middleware(self, app):
        if app.config['DEFAULT_CONTENT_TYPE'] == 'text/html':
            contact_us = app.config['CONTACT_US_URL']
            if contact_us is not None:
                yield ContactRouter(contact_us)

    def on_loaded(self, app):
        if app.callable.command == 'serve':
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
