GAE BLOG
==============

Running on https://luxgaeblog.appspot.com/

Blog application using python google cloud sdk, [lux][] and [AngularJS][].

Features
==============

* Uses Google cloud [ndb](https://cloud.google.com/appengine/docs/python/ndb/) datastore api as object data mapper
* Uses three models: User, Session & Blog
* Models are accessed, created and modified via a [RESTful JSON api](http://quantmindblog.appspot.com/api/)
* Fully responsive interface - built on top of [bootstrap](http://getbootstrap.com/)
* [Fontawesome](http://fortawesome.github.io/Font-Awesome/) icons

Authentication
================

* The web site and the API use two different authentication backends.
* The website uses a session-based backend with [CSRF](http://en.wikipedia.org/wiki/Cross-site_request_forgery) protection for all post data
* The api uses a [JWT](http://self-issued.info/docs/draft-jones-json-web-token-01.html) authentication
* The api and the web applications are handled by the same WSGI application but they can be separated into two different


Dev environment
==================
* Clone lux repository

        git clone git@github.com:quantmind/lux.git

* Move into ``lux/examples`` and run the ``setup.py`` script to install additional python dependencies. These dependencies are listed in the ``requirement.txt``

        python setup.py install

* Run the development server using the ``dev_appserver.py`` script from google cloud sdk:

        dev_appserver.py src --port 6060

* To upload the application into google cloud:

        appcfg.py update gaeblog

Css
=====

To regenerate the ``css`` file issue the command::

    python manage.py style --minify



[node]: https://npmjs.org
[AngularJS]: https://angularjs.org/
[lux]: http://quantmind.github.io/lux/
[GruntJS]: http://gruntjs.com/