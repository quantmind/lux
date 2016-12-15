from asyncio import gather

from lux.utils import test

from tests.auth.user import UserMixin
from tests.auth.password import PasswordMixin
from tests.auth.permissions import PermissionsMixin
from tests.auth.commands import AuthCommandsMixin
from tests.auth.utils import AuthUtils
from tests.auth.registration import RegistrationMixin
from tests.auth.mail_list import MailListMixin
from tests.auth.groups import GroupsMixin
from tests.auth.errors import ErrorsMixin


class TestPostgreSql(test.AppTestCase,
                     AuthUtils,
                     AuthCommandsMixin,
                     UserMixin,
                     PasswordMixin,
                     PermissionsMixin,
                     RegistrationMixin,
                     ErrorsMixin,
                     GroupsMixin,
                     MailListMixin):
    config_file = 'tests.auth'

    @classmethod
    async def beforeAll(cls):
        cls.super_token, cls.pippo_token = await gather(
            cls.user_token('testuser', jwt=cls.admin_jwt),
            cls.user_token('pippo', jwt=cls.admin_jwt)
        )
