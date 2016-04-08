import asyncio

from lux.core import LuxCommand, Setting


class Command(LuxCommand):
    help = "Execute an external command"

    option_list = (
        Setting('commands',
                nargs='+',
                desc='Execute a shall command'),
    )

    async def run(self, options):
        commands = []
        commands.extend(options.commands)
        print(commands)
        proc = await asyncio.create_subprocess_exec(
            *commands, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        await proc.wait()
        data = await proc.stdout.read()
        self.write(data.decode('utf-8').strip())
