'''Script for the google app engine
'''
import environment
import lux

# WSGI application
app = lux.App('blogapp.config').setup()
