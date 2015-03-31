from lux.forms import Field

from .manager import OneToManyRelatedManager, load_relmodel, LazyForeignKey


__all__ = ['ForeignKey', 'CompositeIdField', 'ManyToManyField']


class ForeignKey(Field):
    '''A :class:`.Field` defining a :ref:`one-to-many <one-to-many>`
    objects relationship.
    It requires a positional argument representing the :class:`.Model`
    to which the model containing this field is related. For example::
        class Folder(odm.Model):
            name = odm.CharField()
        class File(odm.Model):
            folder = odm.ForeignKey(Folder, related_name='files')
    To create a recursive relationship, an object that has a many-to-one
    relationship with itself use::
        odm.ForeignKey('self')
    Behind the scenes, the :ref:`odm <odm>` appends ``_id`` to the field
    name to create
    its field name in the back-end data-server. In the above example,
    the database field for the ``File`` model will have a ``folder_id`` field.
    .. attribute:: related_name
        Optional name to use for the relation from the related object
        back to ``self``.
    '''
    index = True
    proxy_class = LazyForeignKey
    related_manager_class = OneToManyRelatedManager

    def __init__(self, model, related_name=None, related_manager_class=None,
                 **kwargs):
        if related_manager_class:
            self.related_manager_class = related_manager_class
        if not model:
            raise FieldError('Model not specified')
        super(ForeignKey, self).__init__(**kwargs)
        self.relmodel = model
        self.related_name = related_name

    def _set_relmodel(self, relmodel, **kw):
        self._relmeta = meta = relmodel._meta
        if (self.related_name not in meta.related and
                self.related_name not in meta.dfields):
            self._relmeta.related[self.related_name] = self
        else:
            raise FieldError('Duplicated related name "{0} in model "{1}" '
                             'and field {2}'.format(self.related_name,
                                                    meta, self))

    def get_store_name(self):
        return '%s_id' % self.name

    def get_value(self, instance, value):
        if isinstance(value, self.relmodel):
            id = value.id
            if id:
                instance['_%s' % self.name] = value
            return id
        else:
            return value

    def to_store(self, instance, store):
        value = super().to_store(instance, store)
        if isinstance(value, self.relmodel):
            return value.id
        else:
            return value

    def register_with_model(self, name, model):
        super().register_with_model(name, model)
        if not model._meta.abstract:
            if not self.related_name:
                self.related_name = '%s_%s_set' % (model._meta.name, self.name)
            # add the RelatedManager proxy to the model holding the field
            setattr(model, self.name, self.proxy_class(self))
            load_relmodel(self, self._set_relmodel)


class CompositeIdField(Field):
    '''This field can be used when an instance of a model is uniquely
    identified by a combination of two or more :class:`Field` in the model
    itself. It requires a number of positional arguments greater or equal 2.
    These arguments must be fields names in the model where the
    :class:`CompositeIdField` is defined.
    .. attribute:: fields
        list of :class:`Field` names which are used to uniquely identify a
        model instance
    Check the :ref:`composite id tutorial <tutorial-compositeid>` for more
    information and tips on how to use it.
    '''
    primary_key = True

    def __init__(self, *fields, **kwargs):
        super(CompositeIdField, self).__init__(**kwargs)
        self.fields = fields
        if len(self.fields) < 2:
            raise FieldError('At least two fields are required by composite '
                             'CompositeIdField')

    def register_with_model(self, name, model):
        fields = []
        for field in self.fields:
            if field not in model._meta.dfields:
                raise FieldError(
                    'Composite id field "%s" not in in "%s" model.' %
                    (field, model._meta))
            field = model._meta.dfields[field]
            fields.append(field)
        self.fields = tuple(fields)
        super().register_with_model(name, model)


class ManyToManyField(Field):
    '''A :ref:`many-to-many <many-to-many>` relationship.
Like :class:`ForeignKey`, it requires a positional argument, the class
to which the model is related and it accepts **related_name** as extra
argument.
.. attribute:: related_name
    Optional name to use for the relation from the related object
    back to ``self``. For example::
        class Group(odm.StdModel):
            name = odm.SymbolField(unique=True)
        class User(odm.StdModel):
            name = odm.SymbolField(unique=True)
            groups = odm.ManyToManyField(Group, related_name='users')
    To use it::
        >>> g = Group(name='developers').save()
        >>> g.users.add(User(name='john').save())
        >>> u.users.add(User(name='mark').save())
    and to remove::
        >>> u.following.remove(User.objects.get(name='john'))
.. attribute:: through
    An optional :class:`StdModel` to use for creating the many-to-many
    relationship can be passed to the constructor, via the **through** keyword.
    If such a model is not passed, under the hood, a :class:`ManyToManyField`
    creates a new *model* with name constructed from the field name
    and the model holding the field. In the example above it would be
    *group_user*.
    This model contains two :class:`ForeignKeys`, one to model holding the
    :class:`ManyToManyField` and the other to the *related_model*.
'''
    def __init__(self, model, through=None, related_name=None, **kwargs):
        self.through = through
        self.relmodel = model
        self.related_name = related_name
        super(ManyToManyField, self).__init__(model, **kwargs)

    def register_with_model(self, name, model):
        super(ManyToManyField, self).register_with_model(name, model)
        if not model._meta.abstract:
            load_relmodel(self, self._set_relmodel)

    def _set_relmodel(self, relmodel):
        relmodel._manytomany_through_model(self)

    def get_store_name(self):
        return None

    def todelete(self):
        return False

    def add_to_fields(self, meta):
        # A many to many field is a dummy field. All it does it provides a
        # proxy for the through model. Remove it from the fields dictionary
        # and addit to the list of many_to_many
        meta.dfields.pop(self.name)
        meta.manytomany.append(self.name)
