import asyncio

from pulsar import Setting

import lux


class Command(lux.Command):
    help = "Execute an external command"

    option_list = (
        Setting('commands',
                nargs='+',
                desc='Execute a shall command'),
    )

    @asyncio.coroutine
    def run(self, options):
        commands = []
        commands.extend(options.commands)
        print(commands)
        proc = yield from asyncio.create_subprocess_exec(
            *commands, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        yield from proc.wait()
        data = yield from proc.stdout.read()
        self.write(data.decode('utf-8').strip())
