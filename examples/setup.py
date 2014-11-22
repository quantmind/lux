#!/usr/bin/env python
'''Setup environment for gaeblog
'''
import time
import os
import sys
import shutil
import subprocess
from os import path


DIR = path.dirname(path.abspath(__file__))
TARGET = os.path.join(DIR, 'gaeblog')
LOCALS = ()


def sh(command, cwd=None):
    return subprocess.Popen(command,
                            #stdout=subprocess.PIPE,
                            #stderr=subprocess.PIPE,
                            shell=True,
                            cwd=cwd,
                            universal_newlines=True).communicate()[0]

def ln(source, target):
    print('Create soft link from %s to %s' % (source, target))
    sh('ln -s %s %s' % (source, target))


def install():
    LIBS = path.join(DIR, 'libs')
    if path.isdir(LIBS):
        print('Removing directory "%s"' % LIBS)
        shutil.rmtree(LIBS)
        time.sleep(1)
    sh('virtualenv libs')
    sh('cp requirements.txt libs/.')
    os.chdir('libs')
    sh('pwd')
    pip = path.join(LIBS, 'bin', 'pip')
    sh('%s install -r requirements.txt' % pip)
    os.chdir(DIR)
    # Create the symlink
    source = os.path.join(LIBS, 'lib/python2.7/site-packages')
    target = os.path.join(TARGET, 'site-packages')
    if path.exists(target):
        os.remove(target)
    ln(source, target)
    #
    # Create lux soft link
    source = os.path.abspath('../lux')
    target = target = os.path.join(TARGET, 'lux')
    ln(source, target)
    #
    # Create lux soft link with luxsite media
    source = os.path.abspath('luxsite/media/luxsite')
    target = target = os.path.join(TARGET, 'blogapp/media/blogapp')
    ln(source, target)

    # And local applications, one directory up from the project directory
    os.chdir(DIR)
    for dep in LOCALS:
        source = os.path.abspath(dep)
        if os.path.isdir(source):
            target = os.path.join(source, dep)
            if os.path.exists(target):
                os.remove(target)
            ln(source, target)
        else:
            print('WARNING: Cannot locate %s' % source)


def runtests():
    try:
        import nose
    except ImportError:
        print('Install nose to run unit tests.')
        exit(1)
    argv = ['nosetests'] + sys.argv[2:]
    argv.extend(('-w', 'tests'))
    src = os.path.join(DIR, 'src')
    if src not in sys.path:
        sys.path.insert(0, src)
    import manage
    nose.run(argv=argv)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            runtests()
        elif sys.argv[1] == 'install':
            install()
        else:
            print('Unknown command %s' % sys.argv[1])
            exit(1)
    else:
        print('Specify a command: install or test')
