<img src="https://assets.quantmind.com/logos/lux/lux-powered.png" alt="Lux powered" width=300>

This directory contains three examples for sites powered by lux. The script to
run the examples is ``manage.py`` in the top level directory.

* A stand-alone website serving HTML content:
```
python manage.py webalone
```
* A stand-alone API site for a JSON-REST API
```
python manage.py webapi
```
* A website serving HTML content which uses the API site for authentication and data
```
python manage.py website
```

# Setup

Before running the services, one need to configure the PostgreSQL database.
This is a one-time operation, from the top level directory type:
```
psql -U postgres -f tests/db.sql
```

Create a virtual environment and install dependencies:
```
pip install virtaulenv myexample
./myexample/bin/pip install -r requirements-dev.txt
```

Set up database tables:
```
# setup migrations
./myexample/bin/python manage.py webalone alembic auto
# initialise tables
./myexample/bin/python manage.py webalone alembic auto -m initial
```
