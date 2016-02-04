import os

from setuptools import setup, find_packages

package_name = 'lux'

try:
    import pulsar  # noqa
    import dateutil  # noqa
    import pytz     # noqa
except ImportError:
    os.environ['lux_install_running'] = 'yes'
    params = {}
else:
    import lux
    params = dict(version=lux.__version__,
                  author=lux.__author__,
                  author_email=lux.__contact__,
                  maintainer_email=lux.__contact__,
                  url=lux.__homepage__,
                  license=lux.__license__,
                  description=lux.__doc__)


def read(name):
    root_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(root_dir, name), 'r') as f:
        return f.read()


def run():
    install_requires = []
    dependency_links = []

    for line in read('requirements.txt').split('\n'):
        if line.startswith('-e '):
            link = line[3:].strip()
            if link == '.':
                continue
            dependency_links.append(link)
            line = link.split('=')[1]
        line = line.strip()
        if line:
            install_requires.append(line)

    packages = find_packages(exclude=['tests', 'tests.*'])

    setup(name=package_name,
          long_description=read('README.rst'),
          packages=packages,
          include_package_data=True,
          zip_safe=False,
          install_requires=install_requires,
          dependency_links=dependency_links,
          scripts=['bin/luxmake.py'],
          classifiers=['Development Status :: 3 - Alpha',
                       'Environment :: Web Environment',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Operating System :: OS Independent',
                       'Programming Language :: JavaScript',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 3.4',
                       'Programming Language :: Python :: 3.5',
                       'Topic :: Utilities'],
          **params)


if __name__ == '__main__':
    run()
