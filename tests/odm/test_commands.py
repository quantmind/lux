from lux.utils import test

from tests.odm.utils import SqliteMixin, OdmUtils


class TestFlushModelsPsql(OdmUtils, test.AppTestCase):

    async def test_flush_models(self):
        cmd = self.fetch_command('flush_models')
        self.assertTrue(cmd.help)
        self.assertEqual(len(cmd.option_list), 2)
        await cmd(['dcsdcds'])
        data = cmd.app.stdout.getvalue()
        self.assertEqual(data.strip().split('\n')[-1],
                         'Nothing done. No models')
        #
        cmd = self.fetch_command('flush_models')
        await cmd(['*', '--dryrun'])
        data = cmd.app.stdout.getvalue()
        self.assertEqual(data.strip().split('\n')[-1],
                         'Nothing done. Dry run')
        #
        cmd = self.fetch_command('flush_models')
        await cmd(['*'], interactive=False, yn='no')
        data = cmd.app.stdout.getvalue()
        self.assertEqual(data.strip().split('\n')[-1],
                         'Nothing done')
        #
        cmd = self.fetch_command('flush_models')
        await cmd(['*'], interactive=False)
        data = cmd.app.stdout.getvalue()
        lines = data.strip().split('\n')
        self.assertTrue(lines)


class TestFlushModelsSqlite(SqliteMixin, TestFlushModelsPsql):
    pass
