import sys


services = set(('webapi', 'website', 'webalone'))


def main():
    from lux.core import execute_from_config

    argv = sys.argv[:]

    if len(argv) == 1:
        argv.append('webalone')

    if argv[1] not in services:
        service = 'webalone'
        argv = argv[1:]
    else:
        service = argv[1]
        argv = argv[2:]

    execute_from_config('example.%s.config' % service, argv=argv)
