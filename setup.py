import os
import sys
import json

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES


def read(fname):
    with open(os.path.join(root_dir, fname)) as f:
        return f.read()


os.environ['lux_setup_running'] = 'yes'
package_name = 'lux'
root_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.join(root_dir, package_name)
pkg = json.loads(read('package.json'))


def requirements():
    req = read('requirements.txt').replace('\r', '').split('\n')
    result = []
    for r in req:
        r = r.replace(' ', '')
        if r:
            result.append(r)
    return result


class osx_install_data(install_data):

    def finalize_options(self):
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)


# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
def get_rel_dir(d, base, res=''):
    if d == base:
        return res
    br, r = os.path.split(d)
    if res:
        r = os.path.join(r, res)
    return get_rel_dir(br, base, r)

packages, data_files = [], []
pieces = fullsplit(root_dir)
if pieces[-1] == '':
    len_root_dir = len(pieces) - 1
else:
    len_root_dir = len(pieces)

for dirpath, _, filenames in os.walk(package_dir):
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)[len_root_dir:]))
    elif filenames and not dirpath.endswith('__pycache__'):
        rel_dir = get_rel_dir(dirpath, package_dir)
        data_files.extend((os.path.join(rel_dir, f) for f in filenames))


def run(argv=None):
    if argv:
        sys.argv = list(argv)
    argv = sys.argv
    command = argv[1] if len(argv) > 1 else None
    params = {'cmdclass': {}}
    if command != 'sdist':
        params['install_requires'] = requirements()
    if sys.platform == "darwin":
        params['cmdclass']['install_data'] = osx_install_data
    else:
        params['cmdclass']['install_data'] = install_data

    setup(name=package_name,
          version=pkg['version'],
          author=pkg['author']['name'],
          author_email=pkg['author']['email'],
          url=pkg['homepage'],
          license=pkg['licenses'][0]['type'],
          description=pkg['description'],
          long_description=read('README.rst'),
          packages=packages,
          package_data={package_name: data_files},
          scripts=['bin/luxmake.py'],
          classifiers=['Development Status :: 2 - Pre-Alpha',
                       'Environment :: Web Environment',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Operating System :: OS Independent',
                       'Programming Language :: JavaScript',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 2.7',
                       'Programming Language :: Python :: 3.3',
                       'Programming Language :: Python :: 3.4',
                       'Topic :: Utilities'],
          **params)


if __name__ == '__main__':
    run()
