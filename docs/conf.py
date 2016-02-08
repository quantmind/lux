# -*- coding: utf-8 -*-
#
import sys, os
os.environ['BUILDING-LUX-DOCS'] = 'yes'
p = lambda x : os.path.split(x)[0]
source_dir = p(os.path.abspath(__file__))
ext_dir = os.path.join(source_dir, '_ext')
docs_dir = p(source_dir)
base_dir = p(docs_dir)

sys.path.insert(0, base_dir)
sys.path.insert(0, ext_dir)
#
import lux
version = lux.__version__
release = version

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))

# -- General configuration -----------------------------------------------------

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.todo',
              'sphinx.ext.extlinks',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode',
              'luxext']

# Beta version is published in github pages
final = True
if 'b' in version:
    final = False
elif 'a' in version:
    final = False
html_context = {'release_version': final}
# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'lux'
pygments_style = 'sphinx'
exclude_trees = []
exclude_patterns = ['notes.md']

def linkcode_resolve(domain, info):
    if domain != 'py':
        return None
    if not info['module']:
        return None
    filename = info['module'].replace('.', '/')
    return 'http://quantmind.github.io/pulsar/%s' % filename


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'lux.tex', 'Lux Documentation',
   'Luca Sbardella', 'manual'),
]

intersphinx_mapping = {
    'python': ('http://python.readthedocs.org/en/latest/', None),
    'pulsar': ('http://quantmind.github.io/pulsar/', None)
}

extlinks = {'django': ('https://www.djangoproject.com/', None),
            'postgresql': ('http://www.postgresql.org/', None),
            'sqlalchemy': ('http://www.sqlalchemy.org/', None),
            'greenlet': ('http://greenlet.readthedocs.org/', None),
            'grunt': ('http://gruntjs.com/', None),
            'nodejs': ('http://nodejs.org/', None)}
