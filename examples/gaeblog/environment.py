import sys
import os

PATH = os.path.dirname(__file__)
SITE_PACKAGES = os.path.join(PATH, 'site-packages')

# Add the site-packages directory to the python path
if os.path.isdir(SITE_PACKAGES) and SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)
