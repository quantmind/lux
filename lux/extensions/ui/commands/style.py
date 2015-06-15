import os

from pulsar.apps.http import HttpClient
from pulsar.utils.pep import native_str
from pulsar.utils.system import convert_bytes
from pulsar import Setting, new_event_loop

from lux.extensions.ui.lib import Css

import lux


class Command(lux.Command):
    help = "Build the style-sheet file from installed applications"
    option_list = (
        Setting('theme', ('--theme',), default='',
                desc='Theme to use. .'),
        Setting('variables', ('--variables',), action='store_true',
                default=False,
                desc=('Dump the theme variables as json'
                      ' file for the theme specified')),
        Setting('cssfile', ('--cssfile',), default='',
                desc=('Target path of css file. For example '
                      '"media/site/site.css". If not provided, '
                      'a file called {{ STYLE }}.css will '
                      'be created and put in "media/<sitename>" '
                      'directory, if available, '
                      'otherwise in the local directory.')),
        Setting('minify', ('--minify',), action='store_true',
                default=False,
                desc='Also create a minified file')
    )

    def run(self, options, dump=True, **params):
        target = options.cssfile
        app = self.app
        name = app.meta.name
        self.theme = options.theme or name
        if not target and not options.variables:
            target = self.theme
            mdir = os.path.join(self.app.meta.path, 'media', name)
            if os.path.isdir(mdir):
                target = os.path.join(mdir, target)
        data = self.render(self.theme, options.variables)
        if dump:
            if target:
                targets = ['%s.css' % target]
                if options.minify:
                    targets.append('%s.min.css' % target)
                for minify, target in enumerate(targets):
                    if minify:
                        data = self.minify(options, data)
                    with open(target, 'w') as f:
                        f.write(data)
                    b = convert_bytes(len(data))
                    self.write('Created %s file. Size %s.' % (target, b))
                return targets
            else:
                self.write(data)
        return data

    def render(self, theme, dump_variables):
        self.write('Building theme "%s".' % theme)
        css = Css(app=self.app)
        return css.dump(theme, dump_variables=dump_variables)

    def minify(self, options, data):
        b = convert_bytes(len(data))
        self.write('Minimise %s css file via http://cssminifier.com' % b)
        http = HttpClient(loop=new_event_loop())
        response = http.post('http://cssminifier.com/raw',
                             encode_multipart=False,
                             data={'input': data})
        if response.status_code == 200:
            return native_str(response.get_content())
        else:
            response.raise_for_status()
