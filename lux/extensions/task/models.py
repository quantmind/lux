'''Models for tracking pulsar tasks and servers.
Requires python-stdnet_

.. _python-stdnet: http://pypi.python.org/pypi/python-stdnet/
'''
import platform
from uuid import uuid4
from datetime import datetime, timedelta
from multiprocessing.queues import Empty

from pulsar import make_async
from pulsar.apps import tasks
from pulsar.utils.timeutils import timedelta_seconds
from pulsar.apps.data import odm

from djpcms.utils.text import nicename
from djpcms.utils.dates import nicetimedelta

__all__ = ['PulsarServer', 'Task', 'JobModel', 'Script', 'Queue']


############################################################################
##    Classes for managing Pulsar Servers
############################################################################
class PulsarServer(odm.StdModel):
    code = odm.SymbolField()
    path = odm.CharField(required=True)
    notes = odm.CharField(required=False)
    location = odm.CharField()

    def __unicode__(self):
        return to_string('{0} - {1}'.format(self.code, self.path))

    def this(self):
        return False
    this.boolean = True


############################################################################
##    Classes for managing Pulsar tasks Job
############################################################################
class JobModel(odm.ModelBase):
    '''A dummy stdnet model for a pulsar Job.'''
    def __init__(self, data=None, proxy=None, **kwargs):
        if not self.id:
            raise ValueError('No id for Job Model')
        self.proxy = proxy
        if data:
            for head in data:
                val = data[head]
                if head == 'run_every' or head == 'next_run':
                    val = nicetimedelta(val)
                setattr(self, head, val)
        self.name = nicename(self.id)

    def __unicode__(self):
        return self.name

    def tasks(self):
        return Task.objects.filter(name=self.id)
