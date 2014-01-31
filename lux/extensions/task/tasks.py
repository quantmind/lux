from collections import Mapping

from pulsar import maybe_failure
from pulsar.apps.tasks import Job, JobMetaClass


__all__ = ['get_job_form',
           'register_job_form',
           'task_form_info',
           'task_message_info',
           'Run_Python_Code',
           'distributed_queue']


############################################################################
##    Registration and Retrieval of Pulsar Job forms
############################################################################

job_forms = {}


def register_job_form(job, form):
    '''Register a :class:`djpcms.forms.Form` for a
:class:`pulsar.apps.tasks.Job` class which can be used to lunch a new task
from the admin interface.'''
    if isinstance(job, Job) or isinstance(job, JobMetaClass):
        job = job.name
    job_forms[job] = form


def get_job_form(instance):
    '''Retrieve a :class:`djpcms.forms.Form` for a
:class:`pulsar.apps.tasks.Job`. If no form is registered wuth the job, it
returns :class:`EmptyJobRunForm`.'''
    if instance and instance.id in job_forms:
        f = job_forms[instance.id]
    else:
        f = EmptyJobRunForm
    return f


def task_form_info(request, form, result):
    '''Information regarding a Task run with links to the Task application
views.

:parameter request: A WSGI djpcms request class
:parameter form: A bound :class:`djpcms.forms.Form` used to run the task.
:parameter request: A WSGI djpcms request class
'''
    f = maybe_failure(result)
    if f is not None:
        return f
    elif isinstance(result, Task):
        id = result.id
    elif result and 'id' in result:
        id = result['id']
    else:
        form.add_error('Could not create task')
        return form
    rt = request.for_model(Task, urlargs={'id': id}, name='view')
    if rt:
        link = html.Widget('a', id, href=rt.url).render(rt)
    else:
        link = res['id']
    form.add_message(link + ' sent to task queue')
    return form


def task_message_info(request, result):
    if is_failure(result):
        return result
    id = None
    if isinstance(result, Task):
        id = result.id
    elif isinstance(result, Mapping) and result and 'id' in result:
        id = result['id']
    if id is not None:
        rt = request.for_model(Task, urlargs={'id': id}, name='view')
        if rt:
            link = html.Widget('a', id, href=rt.url).render(rt)
        else:
            link = res['id']
        return link


############################################################################
##    Run python code on the task queue
############################################################################
class Run_Python_Code(Job):
    '''Run a python script in the task queue. The code must have a callable
named "task_function".'''
    def __call__(self, consumer, code=None, **kwargs):
        if code:
            code = code.replace('\r\n', '\n')
        code_local = compile(code, '<string>', 'exec')
        ns = {}
        exec(code_local, ns)
        func = ns.get('task_function')
        if hasattr(func, '__call__'):
            return func(**kwargs)
        else:
            raise ValueError('task_function is not defined in script, or it '
                             'is not a callable')


class CodeForm(forms.Form):
    code = forms.CharField(widget=html.TextArea(rows=20,
                                                cn='taboverride code'))


register_job_form(
    Run_Python_Code,
    forms.HtmlForm(CodeForm,
                   inputs=(('run', 'run'),),
                   layout=uni.FormLayout(default_style=uni.blockLabels))
)


############################################################################
##    A task queue based on redis list
############################################################################
class distributed_queue(object):
    '''A distributed task queue based on the Queue model'''
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return str(self.instance)

    @property
    def instance(self):
        try:
            return Queue.objects.get(id=self.id)
        except Queue.DoesNotExist:
            return Queue(id=self.id).save()

    @property
    def queue(self):
        return self.instance.queue

    def qsize(self):
        return self._queue.qsize()

    def put(self, elem):
        '''Put item into the queue.'''
        q = self.queue
        q.push_front(elem)
        q.save()

    def get(self, block=True, timeout=None):
        '''Remove and return an item from the queue.
If optional args ``block`` is ``True`` (the default)
and ``timeout`` is ``0`` (the default), block if necessary until
an item is available.
If timeout is a positive number, it blocks at most ``timeout`` seconds.

It raises  and `multiprocessing.queues.Empty` exception
if no item was available.'''
        if block:
            timeout = max(1, int(round(timeout))) if timeout else 0
            ret = self.queue.block_pop_back(timeout)
        else:
            ret = self.queue.pop_back()
        if ret is None:
            raise Empty
        return ret
