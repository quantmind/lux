'''Script for executing lux commands.
Not required by the appengine

Create the style sheet

    python manage.py style --minify
'''
import os
import sys

import environment

APPENGINE_PATHS = ['/usr/local/google_appengine', 'vendors']


for path in APPENGINE_PATHS:
    path = os.path.abspath(path)
    if os.path.isdir(path) and path not in sys.path:
        sys.path.insert(0, path)
        break


if __name__ == '__main__':
    import lux
    lux.execute_from_config('blogapp.config')
