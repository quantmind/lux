from pulsar.utils.pep import iteritems, is_string

from lux import Html


content_types = {}


def apply_content(html, content, context):
    if content.content_type in content_types:
        handler = content_types[content.content_type]
    else:
        handler = content_types['contenttype']
    handler(html, content, context)


class ContentTypeMeta(type):
    '''
    Just a metaclass to differentiate plugins from other classes
    '''
    def __new__(cls, name, bases, attrs):
        new_class = super(ContentTypeMeta, cls).__new__
        if attrs.pop('abstract', None):
            return new_class(cls, name, bases, attrs)
        pname = (attrs.get('name') or name).lower()
        pcls = new_class(cls, name, bases, attrs)
        content_types[pname] = pcls()
        return pcls


class ContentType(ContentTypeMeta('ContentTypeBase', (), {'abstract': True})):

    def __call__(self, html, fields, context):
        html.data('fields', len(fields))
        for name, value in iteritems(fields):
            if is_string(value):
                html.append(Html('div', value, field=name))
            else:
                html.append(Html('div', field=name, value=value))


class ContentUrl(ContentType):

    def __call__(self, html, fields, context):
        if fields.get('content_url') == 'this':
            html.data('fields', 0)
            html.append(context.get('this'))
        else:
            super(ContentUrl, self).__call__(html, fields, context)


class DataTable(ContentType):

    def __call__(self, html, fields, context):
        html.data('fields', 0)
        data = {'col-headers': fields.get('fields'),
                'ajax-url': fields.get('url')}
        html.append(Html('div', cn='datagrid', data=data))
