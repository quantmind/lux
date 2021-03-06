from lux.core import CommandError


class AuthCommandsMixin:

    async def test_create_token(self):
        command = self.app.get_command('create_token')
        self.assertTrue(command.help)
        token = await command(['--username', 'pippo'])
        self.assertTrue(token)

    async def test_create_token_fail(self):
        command = self.app.get_command('create_token')
        self.assertTrue(command.help)
        await self.wait.assertRaises(CommandError, command,
                                     ['--username', 'dfgdgf'])
