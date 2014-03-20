'''Models for Role-based access control (RBAC).
It is an approach for managing users permissions on
your application which could be a web-site, an organisation and so forth.

Introduction
======================
There are five different elements to get familiar with this RBAC
implementation:

* :class:`Role`: within a site, a roles is created for various ``operations``.
* :class:`Permissions`: they represents the power to perform certain
  ``operations`` on a resource and are assigned to specific :class:`Role`.
* ``Operations``: what can a :class:`User` do with that permission, usually,
  ``create``, ``read`` ``update``, ``delete`` (CRUD).
* **Subjects**: these are the system users which are assigned particular
  **roles**.
  Permissions are not assigned directly to **subjects**, instead they are
  acquired through their roles.


The :class:`Permission` to perform certain certain **operations** are assigned
to specific **roles**.

This example is manages Users, Groups and Permissions.

.. rbac-roles

Roles
==============
In this implementation a role is uniquely identified by a ``name`` and
a ``owner``.

.. autoclass:: Role
   :members:
   :member-order: bysource


.. rbac-subject

Subjects
===============
The subject in this implementation is given by the :class:`Group`.
Therefore :ref:`roles <rbac-roles>` are assigned to :class:`Group`. Since roles
are implemented via the :class:`Role` model, the relationship between
:class:`Group` and :class:`Role` is obtained via a
:class:`stdnet.odm.ManyToManyField`.


.. autoclass:: Group
   :members:
   :member-order: bysource

The system user is implemented via the :class:`User`. Since roles are always
assigned to :class:`Group`, a :class:`User` obtains permissions via the#
groups he belongs to.

.. autoclass:: User
   :members:
   :member-order: bysource

Usage
==============
Let's consider a model called ``Photo``.
We want all ``authenticated`` users to be able to `read` instances
of ``Book``::

    role = Role(name='can read Book',
                owner=website)

    role.add_permission(Book, 'read')

For the Photos of a user::

    lsbardel = models.user.get(username='lsbardel')
    role = Role(name='can read lsbardel books',
                owner=lsbardel)
    role.add_permission(Book, 'read')

We want all ``admin`` users to be able to `update` instances from
model ``MyModel`` but not delete them::

    role = Role(name='can create/update my model',
                permission_level=update,
                model=MyModel).save()
    role.groups.add(admin)

When we create a new instance of ``MyModel`` we need to give the required role

    instance = MyModel(....., user=user).save()

    role.add(instance)

Lets assume we have a ``query`` on ``MyModel`` and we need all the instances
for ``user`` with permission ``level``:

    authenticated_query(query, user, level)
'''
from datetime import datetime

from pulsar.utils.log import lazymethod
from pulsar.utils.pep import to_bytes, to_string
from pulsar.apps.data import odm


class PermissionManager(odm.Manager):

    def for_object(self, object, **params):
        if isclass(object):
            qs = self.query(model_type=object)
        else:
            qs = self.query(model_type=object.__class__,
                            object_pk=object.id)
        if params:
            qs = qs.filter(**params)
        return qs


class UserManager(odm.Manager):

    def check_user(self, username, email):
        '''username and email (if provided) must be unique.'''
        avail = yield self.filter(username=username).count()
        if avail:
            raise FieldError('Username %s already in use.' % username)
        if email:
            avail = yield self.filter(email=email).count()
            if avail:
                raise FieldError('Email %s already in use.' % email)

    def create_user(self, username=None, email=None, **params):
        yield self.check_user(username, email)
        yield self.new(username=username, email=email, **params)

    def permitted_query(self, query, group, operations):
        '''Change the ``query`` so that only instances for which
        ``group`` has roles with permission on ``operations`` are returned.
        '''
        session = query.session
        models = session.router
        user = group.user
        if user.is_superuser:   # super-users have all permissions
            return query
        roles = group.roles.query()
        roles = group.roles.query()  # query on all roles for group
        # The throgh model for Role/Permission relationship
        throgh_model = models.role.permissions.model
        models[throgh_model].filter(role=roles,
                                    permission__model_type=query.model,
                                    permission__operations=operations)

        # query on all relevant permissions
        permissions = router.permission.filter(model_type=query.model,
                                               level=operations)

        owner_query = query.filter(user=user)
        # all roles for the query model with appropriate permission level
        roles = models.role.filter(model_type=query.model, level__ge=level)
        # Now we need groups which have these roles
        groups = Role.groups.throughquery(
            session).filter(role=roles).get_field('group')
        # I need to know if user is in any of these groups
        if user.groups.filter(id=groups).count():
            # it is, lets get the model with permissions less
            # or equal permission level
            permitted = models.instancerole.filter(
                role=roles).get_field('object_id')
            return owner_query.union(model.objects.filter(id=permitted))
        else:
            return owner_query


class Subject(object):
    #roles = odm.ManyToManyField('Role', related_name='subjects')

    def create_role(self, name):
        '''Create a new :class:`Role` owned by this :class:`Subject`'''
        models = self.session.router
        return models.role.new(name=name, owner=self)

    def assign(self, role):
        '''Assign :class:`Role` ``role`` to this :class:`Subject`. If this
:class:`Subject` is the :attr:`Role.owner`, this method does nothing.'''
        if role.owner_id != self.id:
            return self.roles.add(role)

    def has_permissions(self, object, group, operations):
        '''Check if this :class:`Subject` has permissions for ``operations``
on an ``object``. It returns the number of valid permissions.'''
        if self.is_superuser:
            return 1
        else:
            models = self.session.router
            # valid permissions
            query = models.permission.for_object(object, operation=operations)
            objects = models[models.role.permissions.model]
            return objects.filter(role=self.role.query(),
                                  permission=query).count()


class User(odm.Model, Subject):
    '''The user of a system.

    The only field required is the :attr:`username`.
    which is also unique across all users.
    '''
    username = odm.CharField(unique=True)
    password = odm.CharField(required=False, hidden=True)
    first_name = odm.CharField(required=False)
    last_name = odm.CharField(required=False)
    email = odm.CharField(unique=True, required=False)
    is_active = odm.BooleanField(default=True)
    can_login = odm.BooleanField(default=True)
    is_superuser = odm.BooleanField(index=True, default=False)
    data = odm.JSONField(required=False)

    manager_class = UserManager

    def __unicode__(self):
        return self.username

    def fullname(self):
        if self.first_name or self.last_name:
            return ' '.join((n for n in (self.first_name,
                                         self.last_name) if n))
        else:
            return ''

    def is_authenticated(self):
        return self.can_login


class Role(odm.Model):
    '''A :class:`Role` is uniquely identified by its :attr:`name` and
:attr:`owner`.'''
    id = odm.CompositeIdField('name', 'owner')
    name = odm.CharField()
    '''The name of this role.'''
    owner = odm.ForeignKey(User, related_name='own_roles')
    '''The owner of this role.'''
    permissions = odm.JSONField(default=list)
    '''the set of all :class:`Permission` assigned to this :class:`Role`.'''
    #users = odm.ManyToManyField(User, related_name='roles')

    def __unicode__(self):
        return self.name

    def add_permission(self, resource, operation):
        '''Add a new :class:`Permission` for ``resource`` to perform an
        ``operation``. The resource can be either an object or a model.'''
        if isclass(resource):
            model_type = resource
            pk = ''
        else:
            model_type = resource.__class__
            pk = resource.id
        model = odm.get_hash_from_model(model_type)
        p = (model, pk, operation)
        if p not in self.permissions:
            self.permissions.append(p)

    def assignto(self, subject):
        '''Assign this :class:`Role` to ``subject``.'''
        return subject.assign(self)


class Group(odm.Model):
    '''A group of users.'''
    name = odm.CharField(unique=True)
    #users = odm.ManyToManyField(User, related_name='groups')
    description = odm.CharField()

    def permission_for_model(self, model):
        qs = tuple(self.permissions.query().filter(
            model_type=model).get_field('numeric_code'))
        if qs:
            return qs[0]

    def __unicode__(self):
        return self.name


class Session(odm.Model):
    '''A session model with a hash table as data store.'''
    serializable = False
    TEST_COOKIE_NAME = 'testcookie'
    TEST_COOKIE_VALUE = 'worked'
    id = odm.CharField(primary_key=True)
    expiry = odm.DateTimeField()
    user = odm.ForeignKey(User)

    @property
    def expired(self):
        return datetime.now() >= self.expiry
