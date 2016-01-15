from importlib import import_module

from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.tables import ListTable
from docutils import io, nodes, statemachine, utils, frontend
from docutils.utils import SystemMessagePropagation

import sphinx


class lux_extension(nodes.General, nodes.Element):
    pass


class LuxExtensionDirective(Directive):
    """
    ExcelTableDirective implements the directive.
    Directive allows to create RST tables from the contents
    of the Excel sheet. The functionality is very similar to
    csv-table (docutils) and xmltable (:mod:`sphinxcontrib.xmltable`).

    Example of the directive:

    .. code-block:: rest

    .. table::
     :datafunction: path.to.my.data.function

    """
    has_content = False
    required_arguments = 1
    option_spec = {'classname': directives.unchanged}

    def run(self):
        """
        Implements the directive
        """
        # Get content and options
        path = self.arguments[0]
        node = lux_extension()
        klass = self.options.get('classname') or 'Extension'
        try:
            module = import_module(path)
            Ext = getattr(module, klass)
            params = list(Ext.meta.config.values())
        except Exception as e:
            document = self.state.document
            return [document.reporter.warning(
                'Could not import Extension from "%s". %s' % (path, e))]
        tab_width = self.options.get(
            'tab-width', self.state.document.settings.tab_width)
        rawdocs = '\n'.join(self.text(params))
        include_lines = statemachine.string2lines(
                rawdocs, tab_width, convert_whitespace=1)
        self.state_machine.insert_input(include_lines, 'lux_extension')
        return []

    def text(self, params):
        for p in sorted(params, key=lambda x: x.name):
            if not p.override:
                yield ''
                yield '.. setting:: %s' % p.name
                yield ''
                yield '%s' % p.name
                yield '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                yield ''
                try:
                    yield 'Default: ``%r``' % str(p.default)
                except Exception as e:
                    yield 'Default: ``%r``' % str(e)
                yield ''
                yield p.doc
                yield ''


def setup(app):
    app.add_directive('lux_extension', LuxExtensionDirective)
    app.add_crossref_type(
        directivename = "setting",
        rolename = "setting",
        indextemplate = "pair: %s; setting",
    )
