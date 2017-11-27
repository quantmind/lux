import smtplib
import ssl

from lux import core

from .message import EmailMultiAlternatives, sanitize_address, DNS_NAME

try:
    from premailer import transform
except ImportError:     # pragma    nocover

    def transform(html_message, base_url=None):
        return html_message

try:
    from bs4 import BeautifulSoup as bs
except ImportError:     # pragma    nocover
    bs = None


class EmailBackend(core.EmailBackend):

    def message(self, sender, to, subject, message, html_message):
        """Prepare an message
        """
        if not isinstance(to, (list, tuple)):
            to = [to]
        if html_message:
            if not message and bs:
                body = bs(html_message, 'html.parser').find('body')
                if body:
                    message = body.get_text().strip()
            html_message = transform(html_message)

        msg = EmailMultiAlternatives(subject, message, sender, to,
                                     encoding=self.app.config['ENCODING'])
        if html_message:
            msg.attach_alternative(html_message, 'text/html')
        return msg

    def send_mails(self, messages):     # pragma    nocover
        '''Send emails in the event loop executor.

        :param messages: list of messages to send
        :return: a Future object
        '''
        return self.app._loop.run_in_executor(
            None, self._send_mails, messages)

    # INTERNALS

    def _send_mails(self, messages):
        num_sent = 0
        try:
            connection = self._open()
            for message in messages:
                num_sent += self._send(connection, message)
            self._close(connection)
        except ConnectionRefusedError:
            self.app.logger.error('Could not connect to mail server',
                                  extra={'mail': True})
        except Exception:
            self.app.logger.exception('Error while sending mail',
                                      extra={'mail': True})
        return num_sent

    def _open(self):    # pragma    nocover
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        cfg = self.app.config
        connection_class = smtplib.SMTP
        # If local_hostname is not specified, socket.getfqdn() gets used.
        # For performance, we use the cached FQDN for local_hostname.
        connection = connection_class(
            cfg['EMAIL_HOST'], cfg['EMAIL_PORT'],
            local_hostname=DNS_NAME.get_fqdn())

        if cfg['EMAIL_USE_TLS']:
            connection.ehlo()
            connection.starttls(keyfile=cfg['EMAIL_TLS_KEYFILE'],
                                certfile=cfg['EMAIL_TLS_CERTFILE'])
            connection.ehlo()

        if cfg['EMAIL_HOST_USER'] and cfg['EMAIL_HOST_PASSWORD']:
            connection.login(cfg['EMAIL_HOST_USER'],
                             cfg['EMAIL_HOST_PASSWORD'])
        return connection

    def _send(self, connection, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        from_email = sanitize_address(email_message.from_email,
                                      email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        message = email_message.message()
        try:
            connection.sendmail(from_email, recipients,
                                message.as_bytes(linesep='\r\n'))
            return 1
        except smtplib.SMTPException:
            self.app.logger.exception('Error while sending message',
                                      extra={'mail': True})
            return 0

    def _close(self, connection):
        """Closes the connection to the email server."""
        try:
            connection.quit()
        except (ssl.SSLError, smtplib.SMTPServerDisconnected):
            # This happens when calling quit() on a TLS connection
            # sometimes, or when the connection was already disconnected
            # by the server.
            connection.close()
        except smtplib.SMTPException:
            self.app.logger.exception(
                'Error while closing connection to SMTP server',
                extra={'mail': True})
