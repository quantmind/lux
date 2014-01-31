'''
Lux :class:`.Template` for HTML grid elements

Grid
=============

.. autoclass:: Grid
   :members:
   :member-order: bysource


Row
=============

.. autoclass:: Row
   :members:
   :member-order: bysource

Column
=============

.. autoclass:: Column
   :members:
   :member-order: bysource
'''
from .content import Template


class Column(Template):
    '''A column is positioned within a :class:`Row`.

    :param span: Optional parameter which set the :attr:`span` attribute.

    .. attribute:: span

        An integer indicating the number of spans the column cover within
        a class:`Row`.
    '''
    tag = 'div'
    classes = 'column'

    def __init__(self, *children, **params):
        self.span = params.pop('span', 1)
        super(Column, self).__init__(*children, **params)
        if self.span > 1:
            raise ValueError('Column span "%s" greater than one!' % self.span)


class GridElement(object):
    '''Signature class for :class:`Grid` child elements such as
    :class:`Row`.
    '''
    pass


class Row(Template, GridElement):
    '''A row is a container of :class:`Column` elements.
    It  must contain at least one :class:`Column`.

    :param column: Optional parameter which set the :attr:`column` attribute.

    .. attribute:: column

        It can be either 12 or 24 and it indicates the number of column
        spans available.

        Default: 24
    '''
    tag = 'div'
    columns = 24

    def __init__(self, *children, **params):
        self.columns = params.pop('columns', self.columns)
        self.classes = 'grid%s row' % self.columns
        super(Row, self).__init__(*children, **params)

    def child_template(self, child=None):
        if not isinstance(child, Column):
            child = Column(child)
        span = int(child.span * self.columns)
        child.classes += ' span%s' % span
        return child


class Grid(Template):
    '''A container of :class:`GridElement`.

    :parameter fixed: optional boolean flag to indicate if the grid is
        fixed (html class ``grid fixed``) or fluid (html class ``grid fluid``).
        If not specified the grid is considered fluid (it changes width when
        the browser window changes width).

    '''
    tag = 'div'

    def html(self, request, context, children, **kwargs):
        html = super(Grid, self).html(request, context, children, **kwargs)
        cn = 'grid fixed' if self.parameters.fixed else 'grid fluid'
        return html.addClass(cn)

    def child_template(self, child=None):
        if not isinstance(child, GridElement):
            child = Row(child)
        return child
