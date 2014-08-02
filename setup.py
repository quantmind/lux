import os
import json

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES

root_dir = os.path.dirname(os.path.abspath(__file__))

def read(fname):
    return open(os.path.join(root_dir, fname)).read()

pkg = json.loads(read('package.json'))
package_dir = os.path.join(root_dir, pkg['name'])

def requirements():
    req = read('requirements.txt').replace('\r','').split('\n')
    result = []
    for r in req:
        r = r.replace(' ','')
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


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

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
    br,r = os.path.split(d)
    if res:
        r = os.path.join(r,res)
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


setup(
        name=pkg['name'],
        version=pkg['version'],
        author=pkg['author']['name'],
        author_email=pkg['author']['email'],
        url=pkg['homepage'],
        license=pkg['licenses'][0]['type'],
        description=pkg['description'],
        long_description=read('README.rst'),
        packages=packages,
        data_files=data_files,
        package_data={pkg['name']: data_files},
        install_requires=requirements(),
        scripts=['bin/luxmake.py'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: JavaScript',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Topic :: Utilities'
        ],
    )
