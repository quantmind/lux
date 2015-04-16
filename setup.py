import os
import json

from setuptools import setup, find_packages

package_name = 'lux'


def read(name):
    root_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(root_dir, name), 'r') as f:
        return f.read()


def run():
    install_requires = []
    dependency_links = []
    pkg = json.loads(read('package.json'))

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
          version=pkg['version'],
          author=pkg['author']['name'],
          author_email=pkg['author']['email'],
          url=pkg['homepage'],
          license=pkg['licenses'][0]['type'],
          description=pkg['description'],
          long_description=read('README.rst'),
          packages=packages,
          include_package_data=True,
          zip_safe=False,
          install_requires=install_requires,
          dependency_links=dependency_links,
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
                       'Topic :: Utilities'])


if __name__ == '__main__':
    run()
