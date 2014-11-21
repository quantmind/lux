'''Script for the google app engine
'''
import environment
import lux

# WSGI application for potatoblog
app = lux.App('blogapp.config').setup()
