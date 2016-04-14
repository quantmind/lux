from setuptools import setup, find_packages

import lux_config as config


def run():
    requires, links = config.requirements('requirements.txt')

    meta = dict(
        name='lux',
        author='Luca Sbardella',
        author_email="luca@quantmind.com",
        maintainer_email="luca@quantmind.com",
        url="https://github.com/quantmind/lux",
        license="BSD",
        long_description=config.read('README.rst'),
        packages=find_packages(exclude=['tests', 'tests.*']),
        include_package_data=True,
        zip_safe=False,
        setup_requires=['pulsar'],
        install_requires=requires,
        dependency_links=links,
        scripts=['bin/luxmake.py'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: JavaScript',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Utilities'
        ]
    )
    setup(**config.setup(meta, 'lux'))


if __name__ == '__main__':
    run()
