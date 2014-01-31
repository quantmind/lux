import os


def nginx_reverse_proxy(site, target=None):
    settings = site.settings
    target = target or '{0}_nginx.conf'.format(settings.SITE_MODULE)
    context = utils.domain_info(settings.DOMAIN_NAME)
    data = '\n'.join(_nginx_stream(settings, context))
    with open(target,'w') as f:
        f.write(data)
    return target


#############################################################
def _nginx_stream(settings, context, logfile=None):
    params = settings.SERVER_CONFIGURATION_PARAMETERS
    redirects = settings.DOMAIN_REDIRECTS
    static_expire = params.get('static_expire','24h')
    secure = context['secure']
    static = application_map(settings.INSTALLED_APPS)
    site_app = static.get(settings.SITE_MODULE)
    if site_app and site_app.exists:
        media_path = site_app.base
    else:
        media_path = None
    # setup redirects
    if secure:
        cpath = settings.HTTPS_CERTIFICATE_PATH
        if not cpath:
            cpath = settings.SITE_DIRECTORY
        # if serving on default port setup a redirect from http to https
        if context['default_port']:
            yield 'server {'
            yield '    listen 80'
            yield '    location / {'
            yield '        rewrite  ^/(.*)$  https://{0[host]}/$1  permanent;'\
                                                .format(context)
            yield '    }\n}\n'
    for redirect in redirects:
        yield 'server {'
        yield '    server_name {0};'.format(redirect)
        yield '    rewrite ^(.*) http://{0[host]}$1 permanent;'.format(context)
        yield '}\n'
    # The actual server
    yield 'server {'
    yield '    listen {0[listen_port]};'.format(context)
    yield '    server_name {0[host]};'.format(context)
    # https boilerplate
    if secure:
        yield '    ssl on;'
        yield '    ssl_certificate {0}/server.crt;'.format(cpath)
        yield '    ssl_certificate_key {0}/server.key;'.format(cpath)
        yield '    ssl_ciphers HIGH:!ADH:!MD5;'
        yield '    ssl_prefer_server_ciphers on;'
        yield '    ssl_protocols TLSv1;'
        yield '    ssl_session_cache shared:SSL:1m;'
        yield '    ssl_session_timeout 5m;'
    if logfile:
        yield   '    access_log {0}'.format(logfile)
    # favicon
    if media_path:
        yield '    '
        yield '    location ~* ^.+\.(ico|txt)$ {'
        yield '        root {0};'.format(media_path)
        yield '        access_log off;'
        yield '        expires {0};'.format(static_expire)
        yield '    }\n'
    # The redirect location
    header_host = '$host'
    if not context['default_port']:
        header_host = '$host:{0[listen_port]}'.format(context)
    yield '    location {0[path]} {{'.format(context)
    yield '        proxy_pass {0[scheme]}://{1};'.format(context,settings.BIND)
    yield '        proxy_redirect off;'
    yield '        proxy_set_header Host {0};'.format(header_host)
    yield '        proxy_set_header X-Real-IP $remote_addr;'
    yield '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;'
    yield '        client_max_body_size 10m;'
    yield '        client_body_buffer_size 128k;'
    yield '        proxy_connect_timeout 90;'
    yield '        proxy_send_timeout 90;'
    yield '        proxy_read_timeout 90;'
    yield '        proxy_buffer_size 4k;'
    yield '        proxy_buffers 4 32k;'
    yield '        proxy_busy_buffers_size 64k;'
    yield '        proxy_temp_file_write_size 64k;'
    yield '    }\n'
    for app in static.values():
        if app.exists:
            yield '    location {0} {{'.format(app.url)
            yield '        root {0};'.format(app.base)
            yield '        expires {0};'.format(static_expire)
            yield '    }\n'
    yield '}'
