import os
import platform

from pulsar import Setting

import lux


class Command(lux.Command):
    option_list = (
        Setting('nginx', ('-n', '--nginx'),
                default='http://{0}'.format(platform.node()),
                desc='Nginx server as http://host or https://host.'),
        Setting('port', ('-p', '--nginx-port'),
                type=int, default=80,
                desc='Nginx server port.'),
        Setting('server', ('-s', '--server'),
                default='http://127.0.0.1:8060',
                desc='Python server as http://host:port.'),
        Setting('target', ('-t', '--target'),
                default='',
                desc='Target path of nginx config file.'),
        Setting('enabled', ('-e', '--enabled'),
                action='store_true',
                default=False,
                desc=('Save the file in the nginx '
                      '/etc/nginx/sites-enabled directory.')),
    )
    help = "Creates a nginx config file for a reverse-proxy configuration."

    def run(self, args, target=None):
        options = self.options(args)
        target = target if target is not None else options.target
        nginx_server = '{0}:{1}'.format(options.nginx, options.port)
        path = None
        if options.enabled and os.name == 'posix':
            path = '/etc/nginx/sites-enabled'
        target = nginx_reverse_proxy_config(self.app,
                                            nginx_server,
                                            proxy_server=options.server,
                                            target=target,
                                            path=path).save()
        self.write('Created nginx configuration file "%s"', target)
        self.write('You need to restart nginx.')
        self.write('in linux /etc/init.d/nginx restart')
