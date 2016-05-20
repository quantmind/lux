from lux.utils import test

from tests.auth.user import UserMixin
from tests.auth.password import PasswordMixin
from tests.auth.odm import OdmMixin
from tests.auth.permissions import PermissionsMixin
from tests.auth.commands import AuthCommands
from tests.auth.utils import AuthUtils
from tests.auth.registration import RegistrationMixin
from tests.auth.mail_list import MailListMixin


class TestSqlite(test.AppTestCase,
                 AuthCommands,
                 UserMixin,
                 OdmMixin,
                 PasswordMixin,
                 PermissionsMixin,
                 RegistrationMixin,
                 MailListMixin,
                 AuthUtils):
    config_file = 'tests.auth'
    config_params = {'DATASTORE': 'sqlite://'}

    su_credentials = {'username': 'bigpippo',
                      'password': 'pluto'}
    user_credentials = {'username': 'littlepippo',
                        'password': 'charon'}

    @classmethod
    def populatedb(cls):
        backend = cls.app.auth_backend
        odm = cls.app.odm()
        backend.create_superuser(cls.app.wsgi_request(),
                                 email='bigpippo@pluto.com',
                                 first_name='Big Pippo',
                                 **cls.su_credentials)
        user = backend.create_user(cls.app.wsgi_request(),
                                   email='littlepippo@charon.com',
                                   first_name='Little Pippo',
                                   active=True,
                                   **cls.user_credentials)

        with odm.begin() as session:
            group = odm.group(name='permission_test')
            secret_group = odm.group(name='secret-readers')
            group.users.append(user)
            session.add(group)
            session.add(secret_group)
            permission = odm.permission(
                name='objective subject',
                description='Can use objective:subject',
                policy={
                    'resource': 'objective:subject',
                    'action': '*'
                })
            group.permissions.append(permission)
            #
            # Create the read permission for secret resource
            spermission = odm.permission(
                name='secret-read',
                description='Can read secret resources',
                policy={
                    'resource': 'secret',
                    'effect': 'allow'
                })
            secret_group.permissions.append(spermission)
