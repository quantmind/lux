#!/usr/bin/env bash

pip install --upgrade pip wheel
pip install --upgrade setuptools
pip install -r requirements-dev.txt
pip install -r requirements.txt
pyslink lux

# temporary
pip install -r ../pulsar/requirements.txt
pyslink ../pulsar/pulsar
pyslink ../pulsar/pulsar_test
pyslink ../pulsar-odm/odm
